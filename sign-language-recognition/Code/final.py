import argparse, os, queue, re, sqlite3, threading, time
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

MODEL_PATH = 'cnn_model_keras2.keras'

parser = argparse.ArgumentParser(description="Live sign language recognition.")
parser.add_argument("--camera", type=int, default=0, help="webcam index (default 0)")
parser.add_argument("--no-voice", action="store_true", help="start with voice off")
args = parser.parse_args()

def die(msg):
	raise SystemExit("ERROR: " + msg)

if not os.path.exists(MODEL_PATH):
	die(MODEL_PATH + " not found in " + os.getcwd() + ". Run this script from the Code/ folder "
		"after training (python cnn_model_train.py). See 'Getting the data and a model' in the README.")
if not os.path.exists("hist"):
	die("'hist' (hand histogram) not found. Run set_hand_histogram.py first to calibrate for your hand.")

class Speaker:
	"""One worker thread owns the pyttsx3 engine; everything else just queues text.
	pyttsx3 is not thread-safe, so the engine is created and used only on that thread."""
	def __init__(self):
		self.q = queue.Queue(maxsize=5)
		self.ready = threading.Event()
		self.ok = False
		threading.Thread(target=self._run, daemon=True).start()
		self.ready.wait(timeout=10)
		if not self.ok:
			print("WARNING: text-to-speech is unavailable; continuing without voice.")

	def _run(self):
		try:
			import pyttsx3
			engine = pyttsx3.init()
			engine.setProperty('rate', 150)
			self.ok = True
		except Exception as e:
			print("WARNING: could not start the speech engine (%s: %s). On Fedora: sudo dnf install espeak-ng"
				% (type(e).__name__, e))
			self.ready.set()
			return
		self.ready.set()
		while True:
			text = self.q.get()
			if text is None:
				break
			try:
				engine.say(text)
				engine.runAndWait()
			except Exception as e:
				print("WARNING: speech failed: %s" % e)

	def say(self, text):
		if not self.ok or not text:
			return
		try:
			self.q.put_nowait(text)
		except queue.Full:
			pass  # drop rather than fall behind the video

	def stop(self):
		if self.ok:
			try:
				self.q.put_nowait(None)
			except queue.Full:
				pass

speaker = Speaker()
model = load_model(MODEL_PATH)

def get_hand_hist():
	# Saved by set_hand_histogram.py as a plain numpy array; allow_pickle=False means
	# an old pickled 'hist' is rejected instead of being executed.
	try:
		return np.load("hist", allow_pickle=False)
	except ValueError:
		die("'hist' is in the old pickle format. Delete it and run set_hand_histogram.py again.")

def get_image_size():
	# Read the input size from the trained model so the dataset is not needed at run time.
	_, height, width, _ = model.input_shape
	return height, width

image_x, image_y = get_image_size()

def keras_process_image(img):
	img = cv2.resize(img, (image_x, image_y))
	img = np.array(img, dtype=np.float32)
	img = np.reshape(img, (1, image_x, image_y, 1))
	return img

# Direct call instead of model.predict(): predict() builds a dataset pipeline on every
# call, which is far too slow inside a per-frame loop. tf.function compiles the call once
# for the fixed 1x50x50x1 input, which is several times faster than an eager call on CPU.
@tf.function(input_signature=[tf.TensorSpec((1, image_x, image_y, 1), tf.float32)])
def infer(x):
	return model(x, training=False)

def keras_predict(model, image):
	processed = keras_process_image(image)
	pred_probab = infer(tf.constant(processed)).numpy()[0]
	pred_class = int(np.argmax(pred_probab))
	return float(pred_probab[pred_class]), pred_class

def load_labels():
	conn = sqlite3.connect("gesture_db.db")
	labels = dict(conn.execute("SELECT g_id, g_name FROM gesture").fetchall())
	conn.close()
	return labels

LABELS = load_labels()

def get_pred_text_from_db(pred_class):
	return LABELS.get(int(pred_class), "")

def get_pred_from_contour(contour, thresh):
	x1, y1, w1, h1 = cv2.boundingRect(contour)
	save_img = thresh[y1:y1+h1, x1:x1+w1]
	text = ""
	if w1 > h1:
		save_img = cv2.copyMakeBorder(save_img, int((w1-h1)/2) , int((w1-h1)/2) , 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
	elif h1 > w1:
		save_img = cv2.copyMakeBorder(save_img, 0, 0, int((h1-w1)/2) , int((h1-w1)/2) , cv2.BORDER_CONSTANT, (0, 0, 0))
	pred_probab, pred_class = keras_predict(model, save_img)
	if pred_probab*100 > 70:
		text = get_pred_text_from_db(pred_class)
	return text

def get_operator(pred_text):
	try:
		pred_text = int(pred_text)
	except:
		return ""
	operator = ""
	if pred_text == 1:
		operator = "+"
	elif pred_text == 2:
		operator = "-"
	elif pred_text == 3:
		operator = "*"
	elif pred_text == 4:
		operator = "/"
	elif pred_text == 5:
		operator = "%"
	elif pred_text == 6:
		operator = "**"
	elif pred_text == 7:
		operator = ">>"
	elif pred_text == 8:
		operator = "<<"
	elif pred_text == 9:
		operator = "&"
	elif pred_text == 0:
		operator = "|"
	return operator

CALC_RE = re.compile(r'^(\d+)(\*\*|>>|<<|[-+*/%&|])(\d+)$')

def safe_calc(expr):
	"""Evaluate '<number><operator><number>' as built by calculator mode. Anything else is
	rejected, so no arbitrary code is ever evaluated."""
	m = CALC_RE.match(expr)
	if not m:
		raise ValueError("unsupported expression")
	a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
	if op == '+': return a + b
	if op == '-': return a - b
	if op == '*': return a * b
	if op == '/': return a / b
	if op == '%': return a % b
	if op == '&': return a & b
	if op == '|': return a | b
	if op in ('**', '<<') and b > 64:
		raise ValueError("number too large")
	if op == '**': return a ** b
	if op == '<<': return a << b
	if op == '>>': return a >> b

hist = get_hand_hist()
x, y, w, h = 300, 100, 300, 300
is_voice_on = not args.no_voice

class FPS:
	def __init__(self):
		self.last = time.perf_counter()
		self.value = 0.0
	def tick(self):
		now = time.perf_counter()
		dt, self.last = now - self.last, now
		if dt > 0:
			self.value = 1.0 / dt if self.value == 0 else 0.9 * self.value + 0.1 / dt
		return self.value

fps = FPS()

def read_frame(cam):
	ok, img = cam.read()
	if not ok or img is None:
		print("ERROR: camera stopped returning frames. Exiting.")
		return None
	return img

def draw_fps(img):
	cv2.putText(img, "FPS: %.1f" % fps.tick(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

def get_img_contour_thresh(img):
	img = cv2.flip(img, 1)
	imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	dst = cv2.calcBackProject([imgHSV], [0, 1], hist, [0, 180, 0, 256], 1)
	disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))
	cv2.filter2D(dst,-1,disc,dst)
	blur = cv2.GaussianBlur(dst, (11,11), 0)
	blur = cv2.medianBlur(blur, 15)
	thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
	thresh = cv2.merge((thresh,thresh,thresh))
	thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
	thresh = thresh[y:y+h, x:x+w]
	contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
	return img, contours, thresh

def say_text(text):
	if is_voice_on:
		speaker.say(text)

def calculator_mode(cam):
	global is_voice_on
	flag = {"first": False, "operator": False, "second": False, "clear": False}
	count_same_frames = 0
	first, operator, second = "", "", ""
	pred_text = ""
	calc_text = ""
	info = "Enter first number"
	say_text(info)
	count_clear_frames = 0
	while True:
		img = read_frame(cam)
		if img is None:
			return 0
		img = cv2.resize(img, (640, 480))
		img, contours, thresh = get_img_contour_thresh(img)
		old_pred_text = pred_text
		if len(contours) > 0:
			contour = max(contours, key = cv2.contourArea)
			if cv2.contourArea(contour) > 10000:
				pred_text = get_pred_from_contour(contour, thresh)
				if old_pred_text == pred_text:
					count_same_frames += 1
				else:
					count_same_frames = 0

				if pred_text == "C":
					if count_same_frames > 5:
						count_same_frames = 0
						first, second, operator, pred_text, calc_text = '', '', '', '', ''
						flag['first'], flag['operator'], flag['second'], flag['clear'] = False, False, False, False
						info = "Enter first number"
						say_text(info)

				elif pred_text == "Best of Luck " and count_same_frames > 15:
					count_same_frames = 0
					if flag['clear']:
						first, second, operator, pred_text, calc_text = '', '', '', '', ''
						flag['first'], flag['operator'], flag['second'], flag['clear'] = False, False, False, False
						info = "Enter first number"
						say_text(info)
					elif second != '':
						flag['second'] = True
						info = "Clear screen"
						#say_text(info)
						second = ''
						flag['clear'] = True
						try:
							calc_text += "= "+str(safe_calc(calc_text))
						except:
							calc_text = "Invalid operation"
						if is_voice_on:
							speech = calc_text
							speech = speech.replace('-', ' minus ')
							speech = speech.replace('/', ' divided by ')
							speech = speech.replace('**', ' raised to the power ')
							speech = speech.replace('*', ' multiplied by ')
							speech = speech.replace('%', ' mod ')
							speech = speech.replace('>>', ' bitwise right shift ')
							speech = speech.replace('<<', ' bitwise leftt shift ')
							speech = speech.replace('&', ' bitwise and ')
							speech = speech.replace('|', ' bitwise or ')
							say_text(speech)
					elif first != '':
						flag['first'] = True
						info = "Enter operator"
						say_text(info)
						first = ''

				elif pred_text != "Best of Luck " and pred_text.isnumeric():
					if flag['first'] == False:
						if count_same_frames > 15:
							count_same_frames = 0
							say_text(pred_text)
							first += pred_text
							calc_text += pred_text
					elif flag['operator'] == False:
						operator = get_operator(pred_text)
						if count_same_frames > 15:
							count_same_frames = 0
							flag['operator'] = True
							calc_text += operator
							info = "Enter second number"
							say_text(info)
							operator = ''
					elif flag['second'] == False:
						if count_same_frames > 15:
							say_text(pred_text)
							second += pred_text
							calc_text += pred_text
							count_same_frames = 0	

		if count_clear_frames == 30:
			first, second, operator, pred_text, calc_text = '', '', '', '', ''
			flag['first'], flag['operator'], flag['second'], flag['clear'] = False, False, False, False
			info = "Enter first number"
			say_text(info)
			count_clear_frames = 0

		blackboard = np.zeros((480, 640, 3), dtype=np.uint8)
		cv2.putText(blackboard, "Calculator Mode", (100, 50), cv2.FONT_HERSHEY_TRIPLEX, 1.5, (255, 0,0))
		cv2.putText(blackboard, "Predicted text- " + pred_text, (30, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 0))
		cv2.putText(blackboard, "Operator " + operator, (30, 140), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 127))
		cv2.putText(blackboard, calc_text, (30, 240), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 255, 255))
		cv2.putText(blackboard, info, (30, 440), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 255) )
		if is_voice_on:
			cv2.putText(blackboard, " ", (450, 440), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 127, 0))
		else:
			cv2.putText(blackboard, " ", (450, 440), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 127, 0))
		cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
		draw_fps(img)
		res = np.hstack((img, blackboard))
		cv2.imshow("Recognizing gesture", res)
		cv2.imshow("thresh", thresh)
		keypress = cv2.waitKey(1) & 0xFF
		if keypress == ord('q') or keypress == ord('c'):
			break
		if keypress == ord('v') and is_voice_on:
			is_voice_on = False
		elif keypress == ord('v') and not is_voice_on:
			is_voice_on = True

	if keypress == ord('c'):
		return 1
	else:
		return 0

def text_mode(cam):
	global is_voice_on
	text = ""
	word = ""
	count_same_frame = 0
	while True:
		img = read_frame(cam)
		if img is None:
			return 0
		img = cv2.resize(img, (640, 480))
		img, contours, thresh = get_img_contour_thresh(img)
		old_text = text
		if len(contours) > 0:
			contour = max(contours, key = cv2.contourArea)
			if cv2.contourArea(contour) > 10000:
				text = get_pred_from_contour(contour, thresh)
				if old_text == text:
					count_same_frame += 1
				else:
					count_same_frame = 0

				if count_same_frame > 20:
					if len(text) == 1:
						say_text(text)
					word = word + text
					if word.startswith('I/Me '):
						word = word.replace('I/Me ', 'I ')
					elif word.endswith('I/Me '):
						word = word.replace('I/Me ', 'me ')
					count_same_frame = 0

			elif cv2.contourArea(contour) < 1000:
				if word != '':
					#print('yolo')
					#say_text(text)
					say_text(word)
				text = ""
				word = ""
		else:
			if word != '':
				#print('yolo1')
				#say_text(text)
				say_text(word)
			text = ""
			word = ""
		blackboard = np.zeros((480, 640, 3), dtype=np.uint8)
		cv2.putText(blackboard, " ", (180, 50), cv2.FONT_HERSHEY_TRIPLEX, 1.5, (255, 0,0))
		cv2.putText(blackboard, "Predicted text- " + text, (30, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 0))
		cv2.putText(blackboard, word, (30, 240), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 255, 255))
		if is_voice_on:
			cv2.putText(blackboard, " ", (450, 440), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 127, 0))
		else:
			cv2.putText(blackboard, " ", (450, 440), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 127, 0))
		cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
		draw_fps(img)
		res = np.hstack((img, blackboard))
		cv2.imshow("Recognizing gesture", res)
		cv2.imshow("thresh", thresh)
		keypress = cv2.waitKey(1) & 0xFF
		if keypress == ord('q') or keypress == ord('t'):
			break
		if keypress == ord('v') and is_voice_on:
			is_voice_on = False
		elif keypress == ord('v') and not is_voice_on:
			is_voice_on = True

	if keypress == ord('t'):
		return 2
	else:
		return 0

def recognize(camera):
	cam = cv2.VideoCapture(camera)
	if not cam.isOpened() or not cam.read()[0]:
		die("could not read from camera %d. Try another index with --camera." % camera)
	keypress = 1
	try:
		while True:
			if keypress == 1:
				keypress = text_mode(cam)
			elif keypress == 2:
				keypress = calculator_mode(cam)
			else:
				break
	finally:
		cam.release()
		cv2.destroyAllWindows()
		speaker.stop()

if __name__ == "__main__":
	keras_predict(model, np.zeros((50, 50), dtype = np.uint8))  # warm-up
	recognize(args.camera)
