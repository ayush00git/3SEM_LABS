import argparse
import cv2
import numpy as np
import hand_segment as HS

BOX_X, BOX_Y = 300, 100   # same hand box as final.py and create_gestures.py

HELP = [
	"b: capture background (box EMPTY) - optional, helps a lot",
	"c: capture hand (cover all small squares)",
	"s: save    q: quit without saving",
]

def open_camera(index):
	cam = cv2.VideoCapture(index)
	if not cam.isOpened() or not cam.read()[0]:
		raise SystemExit("ERROR: could not read from camera %d. Try another index with --camera." % index)
	return cam

def get_hand_hist(camera):
	cam = open_camera(camera)
	skin_px, bg_px, hist = None, None, None
	print("1. Take your hand out of the green box and press 'b' (background).")
	print("2. Cover all the small squares with your hand and press 'c'.")
	print("3. Check the 'Thresh' window shows a clean white hand on black, then press 's'.")
	while True:
		ok, img = cam.read()
		if not ok:
			print("ERROR: camera stopped returning frames.")
			break
		img = cv2.resize(cv2.flip(img, 1), (640, 480))
		clean = img.copy()          # sample from this; never from a frame with drawings on it

		keypress = cv2.waitKey(1) & 0xFF
		if keypress == ord('b'):
			bg_px = clean[BOX_Y:BOX_Y+HS.BOX, BOX_X:BOX_X+HS.BOX].reshape(-1, 3)
			print("Background captured.")
			if skin_px is not None:
				hist = HS.build_hist(skin_px, bg_px)
		elif keypress == ord('c'):
			skin_px = HS.squares_pixels(clean, BOX_X, BOX_Y)
			hist = HS.build_hist(skin_px, bg_px)
			print("Hand captured%s." % ("" if bg_px is not None else " (no background yet: press 'b' with the box empty to improve it)"))
		elif keypress == ord('s'):
			if hist is None:
				print("Press 'c' to capture your hand first, then 's' to save.")
			else:
				break
		elif keypress == ord('q'):
			hist = None
			break

		if hist is not None:
			cv2.imshow("Thresh", HS.mask(clean, hist, BOX_X, BOX_Y))
		cv2.rectangle(img, (BOX_X, BOX_Y), (BOX_X+HS.BOX, BOX_Y+HS.BOX), (0, 255, 0), 2)
		HS.draw_squares(img, BOX_X, BOX_Y)
		state = "background: %s   hand: %s" % ("yes" if bg_px is not None else "no", "yes" if skin_px is not None else "no")
		for i, line in enumerate(HELP + [state]):
			cv2.putText(img, line, (10, 412 + 18 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
		cv2.imshow("Set hand histogram", img)
	cam.release()
	cv2.destroyAllWindows()
	if hist is None:
		print("No calibration saved.")
		return
	HS.save_hist("hist", hist)
	print("Saved hist")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Calibrate hand segmentation for your skin, camera and room.")
	parser.add_argument("--camera", type=int, default=0, help="webcam index (default 0)")
	get_hand_hist(parser.parse_args().camera)
