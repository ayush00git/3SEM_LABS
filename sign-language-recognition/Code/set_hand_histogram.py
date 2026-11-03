import argparse
import cv2
import numpy as np

def build_squares(img):
	x, y, w, h = 420, 140, 10, 10
	d = 10
	imgCrop = None
	crop = None
	for i in range(10):
		for j in range(5):
			if imgCrop is None:
				imgCrop = img[y:y+h, x:x+w]
			else:
				imgCrop = np.hstack((imgCrop, img[y:y+h, x:x+w]))
			cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 1)
			x+=w+d
		if crop is None:
			crop = imgCrop
		else:
			crop = np.vstack((crop, imgCrop))
		imgCrop = None
		x = 420
		y+=h+d
	return crop

def open_camera(index):
	cam = cv2.VideoCapture(index)
	if not cam.isOpened() or not cam.read()[0]:
		raise SystemExit("ERROR: could not read from camera %d. Try another index with --camera." % index)
	return cam

def get_hand_hist(camera):
	cam = open_camera(camera)
	hist = None
	imgCrop = None
	print("Cover all the green squares with your hand, press 'c' to capture, check the Thresh "
		"window, then press 's' to save. Press 'q' to quit without saving.")
	while True:
		ok, img = cam.read()
		if not ok:
			print("ERROR: camera stopped returning frames.")
			break
		img = cv2.flip(img, 1)
		img = cv2.resize(img, (640, 480))
		hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

		keypress = cv2.waitKey(1) & 0xFF
		if keypress == ord('c') and imgCrop is not None:
			hsvCrop = cv2.cvtColor(imgCrop, cv2.COLOR_BGR2HSV)
			hist = cv2.calcHist([hsvCrop], [0, 1], None, [180, 256], [0, 180, 0, 256])
			cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
		elif keypress == ord('s'):
			if hist is None:
				print("Press 'c' to capture your hand first, then 's' to save.")
			else:
				break
		elif keypress == ord('q'):
			hist = None
			break
		if hist is not None:
			dst = cv2.calcBackProject([hsv], [0, 1], hist, [0, 180, 0, 256], 1)
			disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))
			cv2.filter2D(dst,-1,disc,dst)
			blur = cv2.GaussianBlur(dst, (11,11), 0)
			blur = cv2.medianBlur(blur, 15)
			ret,thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
			thresh = cv2.merge((thresh,thresh,thresh))
			cv2.imshow("Thresh", thresh)
		imgCrop = build_squares(img)
		cv2.imshow("Set hand histogram", img)
	cam.release()
	cv2.destroyAllWindows()
	if hist is None:
		print("No histogram saved.")
		return
	# Plain numpy array, not a pickle: loading it can never run code.
	with open("hist", "wb") as f:
		np.save(f, hist, allow_pickle=False)
	print("Saved hist")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Calibrate the hand skin histogram.")
	parser.add_argument("--camera", type=int, default=0, help="webcam index (default 0)")
	get_hand_hist(parser.parse_args().camera)
