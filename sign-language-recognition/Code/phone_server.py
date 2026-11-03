"""Use a phone as the camera and the screen.

The laptop runs this server; the phone opens the printed https:// address in its browser.
The phone sends camera frames, the laptop segments the hand and runs the CNN exactly as
final.py does, and the phone shows the prediction, the word being built and the hand mask,
and speaks the words. Phone and laptop must be on the same Wi-Fi. Run from Code/.

Phone browsers only allow camera access over HTTPS, so a self-signed certificate is created
on first run (needs the openssl command). The phone will warn about it once: choose
"Advanced" -> "Proceed".
"""
import argparse, base64, ipaddress, json, os, socket, sqlite3, ssl, subprocess, threading, time
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

MODEL_PATH = 'cnn_model_keras2.keras'
HIST_PATH = 'hist_phone'          # separate from the laptop 'hist': different camera, different colours
CERT_DIR = 'phone_cert'
PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'phone', 'index.html')
BOX = 300                         # hand box size in pixels, same as final.py
MAX_BODY = 2 * 1024 * 1024

def die(msg):
	raise SystemExit("ERROR: " + msg)

if not os.path.exists(MODEL_PATH):
	die(MODEL_PATH + " not found. Run this from the Code/ folder.")

model = load_model(MODEL_PATH)
_, image_x, image_y, _ = model.input_shape

@tf.function(input_signature=[tf.TensorSpec((1, image_x, image_y, 1), tf.float32)])
def infer(x):
	return model(x, training=False)

conn = sqlite3.connect("gesture_db.db")
LABELS = dict(conn.execute("SELECT g_id, g_name FROM gesture").fetchall())
conn.close()

lock = threading.Lock()           # one frame at a time through OpenCV/TF state
hist = None
if os.path.exists(HIST_PATH):
	try:
		hist = np.load(HIST_PATH, allow_pickle=False)
	except ValueError:
		print("WARNING: %s is not a numpy array; calibrate again from the phone." % HIST_PATH)

def decode(body):
	img = cv2.imdecode(np.frombuffer(body, np.uint8), cv2.IMREAD_COLOR)
	if img is None:
		raise ValueError("not an image")
	return img

def box_from_query(q, img):
	h, w = img.shape[:2]
	x, y = int(q.get('x', ['-1'])[0]), int(q.get('y', ['-1'])[0])
	if x < 0 or y < 0 or x + BOX > w or y + BOX > h:
		raise ValueError("hand box outside the frame")
	return x, y

def segment(img, x, y):
	"""Same steps as final.py get_img_contour_thresh. The phone already mirrors the
	front camera, so there is no flip here."""
	imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	dst = cv2.calcBackProject([imgHSV], [0, 1], hist, [0, 180, 0, 256], 1)
	disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
	cv2.filter2D(dst, -1, disc, dst)
	blur = cv2.GaussianBlur(dst, (11, 11), 0)
	blur = cv2.medianBlur(blur, 15)
	thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
	thresh = thresh[y:y+BOX, x:x+BOX]
	contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
	return thresh, contours

def predict(thresh, contour):
	"""Same crop, padding and 70% rule as final.py get_pred_from_contour."""
	x1, y1, w1, h1 = cv2.boundingRect(contour)
	img = thresh[y1:y1+h1, x1:x1+w1]
	if w1 > h1:
		img = cv2.copyMakeBorder(img, int((w1-h1)/2), int((w1-h1)/2), 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
	elif h1 > w1:
		img = cv2.copyMakeBorder(img, 0, 0, int((h1-w1)/2), int((h1-w1)/2), cv2.BORDER_CONSTANT, (0, 0, 0))
	img = cv2.resize(img, (image_x, image_y)).astype(np.float32).reshape(1, image_x, image_y, 1)
	probs = infer(tf.constant(img)).numpy()[0]
	top = np.argsort(probs)[::-1][:3]
	best = int(top[0])
	text = LABELS.get(best, "") if probs[best] > 0.7 else ""
	return text, float(probs[best]), [[LABELS.get(int(i), str(i)), round(float(probs[i]), 3)] for i in top]

def png_data_url(gray, size=150):
	ok, buf = cv2.imencode('.png', cv2.resize(gray, (size, size), interpolation=cv2.INTER_AREA))
	return "data:image/png;base64," + base64.b64encode(buf.tobytes()).decode()

def handle_predict(img, x, y):
	if hist is None:
		return {"ok": False, "error": "calibrate"}
	thresh, contours = segment(img, x, y)
	out = {"ok": True, "hand": "none", "text": "", "conf": 0.0, "top": [], "mask": png_data_url(thresh)}
	if contours:
		contour = max(contours, key=cv2.contourArea)
		area = cv2.contourArea(contour)
		if area > 10000:
			out["hand"] = "present"
			out["text"], out["conf"], out["top"] = predict(thresh, contour)
		elif area >= 1000:
			out["hand"] = "small"
	return out

def handle_calibrate(img, x, y):
	"""Same 5x10 grid of 10px squares as set_hand_histogram.py, placed at the same spot
	inside the hand box (120, 40 from its top-left corner)."""
	global hist
	sx, sy = x + 120, y + 40
	rows = []
	for i in range(10):
		yy = sy + i * 20
		rows.append(np.hstack([img[yy:yy+10, sx + j*20:sx + j*20 + 10] for j in range(5)]))
	crop = np.vstack(rows)
	h = cv2.calcHist([cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)], [0, 1], None, [180, 256], [0, 180, 0, 256])
	cv2.normalize(h, h, 0, 255, cv2.NORM_MINMAX)
	hist = h
	with open(HIST_PATH, "wb") as f:
		np.save(f, hist, allow_pickle=False)
	thresh, _ = segment(img, x, y)
	return {"ok": True, "mask": png_data_url(thresh)}

class Handler(BaseHTTPRequestHandler):
	timeout = 30   # drop idle or stuck connections

	def log_message(self, *args):
		pass

	def send(self, code, body, ctype):
		self.send_response(code)
		self.send_header("Content-Type", ctype)
		self.send_header("Content-Length", str(len(body)))
		self.send_header("Cache-Control", "no-store")
		self.end_headers()
		self.wfile.write(body)

	def do_GET(self):
		if urlparse(self.path).path != "/":
			return self.send(404, b"not found", "text/plain")
		with open(PAGE, "rb") as f:
			self.send(200, f.read(), "text/html; charset=utf-8")

	def do_POST(self):
		url = urlparse(self.path)
		if url.path not in ("/predict", "/calibrate"):
			return self.send(404, b"not found", "text/plain")
		n = int(self.headers.get("Content-Length", 0))
		if not 0 < n <= MAX_BODY:
			return self.send(413, b"bad size", "text/plain")
		try:
			img = decode(self.rfile.read(n))
			x, y = box_from_query(parse_qs(url.query), img)
			t = time.perf_counter()
			with lock:
				out = (handle_predict if url.path == "/predict" else handle_calibrate)(img, x, y)
			out["ms"] = round((time.perf_counter() - t) * 1000, 1)
		except ValueError as e:
			out = {"ok": False, "error": str(e)}
		self.send(200, json.dumps(out).encode(), "application/json")

class Server(ThreadingHTTPServer):
	daemon_threads = True

	def handle_error(self, request, client_address):
		# Phones close connections and reject the self-signed certificate until the user
		# accepts it; those are normal, not worth a traceback.
		import sys
		if not isinstance(sys.exc_info()[1], (ssl.SSLError, ConnectionError, TimeoutError, socket.timeout)):
			super().handle_error(request, client_address)

def lan_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.connect(("10.255.255.255", 1))   # no packet is sent; this only picks the outgoing interface
		return s.getsockname()[0]
	except OSError:
		return "127.0.0.1"
	finally:
		s.close()

def ensure_cert(ip):
	crt, key = os.path.join(CERT_DIR, "cert.pem"), os.path.join(CERT_DIR, "key.pem")
	if os.path.exists(crt) and os.path.exists(key):
		return crt, key
	os.makedirs(CERT_DIR, exist_ok=True)
	san = "subjectAltName=DNS:localhost,IP:127.0.0.1"
	try:
		ipaddress.ip_address(ip)
		san += ",IP:" + ip
	except ValueError:
		pass
	try:
		subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "825",
			"-keyout", key, "-out", crt, "-subj", "/CN=sign-language-phone", "-addext", san],
			check=True, capture_output=True)
	except FileNotFoundError:
		die("the 'openssl' command is needed to make an HTTPS certificate "
			"(Ubuntu/Fedora: install the openssl package; Windows: use the one in Git for Windows).")
	return crt, key

def main():
	parser = argparse.ArgumentParser(description="Use your phone's camera and screen for live recognition.")
	parser.add_argument("--port", type=int, default=8443)
	parser.add_argument("--host", default="0.0.0.0", help="address to listen on (default: all)")
	args = parser.parse_args()
	ip = lan_ip()
	crt, key = ensure_cert(ip)
	server = Server((args.host, args.port), Handler)
	ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	ctx.load_cert_chain(crt, key)
	# Handshake lazily in the request thread, so a slow phone can't block the accept loop.
	server.socket = ctx.wrap_socket(server.socket, server_side=True, do_handshake_on_connect=False)
	infer(tf.zeros((1, image_x, image_y, 1)))   # warm-up
	print("\nOn your phone (same Wi-Fi), open:\n\n    https://%s:%d\n" % (ip, args.port))
	print("Your phone will warn that the connection is not private (self-signed certificate).")
	print("Tap Advanced -> Proceed. Then allow camera access.")
	print("Calibration: %s" % ("loaded from " + HIST_PATH if hist is not None else "not done yet, do it on the phone"))
	print("Press Ctrl+C here to stop.\n")
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print("Stopped.")

if __name__ == "__main__":
	main()
