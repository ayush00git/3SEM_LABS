"""Skin-colour hand segmentation, shared by set_hand_histogram.py, create_gestures.py,
final.py and phone_server.py.

Calibration builds a colour lookup table (saved as 'hist'): for every hue/saturation pair,
how likely that colour is to be your hand. Compared with the original version it:

- samples skin from a clean frame (the original sampled the frame after drawing the green
  guide squares on it, so 3.8% of the "skin" was pure green and became the histogram peak,
  squashing real skin to about 27/255);
- optionally learns the empty background too, so background colours close to skin are
  pushed down instead of lighting up;
- smooths the histogram, so camera noise still lands on skin instead of on empty bins;
- ignores very dark pixels, whose hue is just noise;
- averages the neighbourhood instead of summing it (the old 10x10 sum turned a background
  value of 4/255 into 255) and uses a fixed threshold instead of Otsu (Otsu always splits the
  image, so an empty box still produced a "hand").

The blur and median steps that give the masks their shape are unchanged, so masks still look
like the training images. The file is a plain float32 numpy array (180 rows of hue x 256 of
saturation, plus one marker row), saved and loaded with allow_pickle=False.
"""
import cv2
import numpy as np

V_MIN = 40            # pixels darker than this (0-255) have meaningless hue; never "hand"
THRESH = 60             # fixed mask threshold on the smoothed 0-255 hand likelihood (tuned on test scenes)
SIGMA_H, SIGMA_S = 2.0, 6.0   # histogram smoothing, in hue (0-179) and saturation (0-255) units
BOX = 300
DISC = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10)).astype(np.float32)
DISC /= DISC.sum()

# The 5x10 grid of 10px squares used for calibration, relative to the hand box's top-left corner
# (same place as the original: x 420.., y 140.. with the box at 300, 100).
SQUARES = [(120 + j * 20, 40 + i * 20) for i in range(10) for j in range(5)]

def squares_pixels(img, box_x, box_y):
	"""BGR pixels under the calibration squares, from a frame with NOTHING drawn on it."""
	return np.vstack([img[box_y+dy:box_y+dy+10, box_x+dx:box_x+dx+10].reshape(-1, 3) for dx, dy in SQUARES])

def draw_squares(img, box_x, box_y):
	for dx, dy in SQUARES:
		cv2.rectangle(img, (box_x+dx, box_y+dy), (box_x+dx+10, box_y+dy+10), (0, 255, 0), 1)

def _hs_hist(bgr_pixels):
	hsv = cv2.cvtColor(bgr_pixels.reshape(-1, 1, 3).astype(np.uint8), cv2.COLOR_BGR2HSV).reshape(-1, 3)
	hsv = hsv[hsv[:, 2] >= V_MIN]
	h = np.zeros((180, 256), np.float32)
	np.add.at(h, (hsv[:, 0], hsv[:, 1]), 1)
	# Smooth; hue is circular (179 is next to 0, and skin sits right at that seam).
	k = int(3 * SIGMA_H) + 1
	h = np.vstack([h[-k:], h, h[:k]])
	h = cv2.GaussianBlur(h, (0, 0), sigmaX=SIGMA_S, sigmaY=SIGMA_H, borderType=cv2.BORDER_REPLICATE)[k:-k]
	return h / max(len(hsv), 1)

def build_hist(skin_pixels, background_pixels=None):
	"""Lookup table (180x256, float32, 0-255) of how hand-like each hue/saturation is."""
	skin = _hs_hist(skin_pixels)
	# Scale so a typical skin colour from the sample maps to 1: the median likelihood of the
	# sampled pixels. Using the maximum instead lets one bright bin squash the rest.
	hsv = cv2.cvtColor(skin_pixels.reshape(-1, 1, 3).astype(np.uint8), cv2.COLOR_BGR2HSV).reshape(-1, 3)
	hsv = hsv[hsv[:, 2] >= V_MIN]
	ref = np.median(skin[hsv[:, 0], hsv[:, 1]]) if len(hsv) else skin.max()
	lut = np.clip(skin / max(ref, 1e-12), 0, 1)
	if background_pixels is not None and len(background_pixels):
		bg = _hs_hist(background_pixels)
		lut *= skin / (skin + bg + 1e-12)        # P(hand | colour), equal priors
	return (lut * 255).astype(np.float32)

FORMAT_VERSION = 2   # stored in an extra last row, so old-style files are recognised and refused

def save_hist(path, hist):
	marker = np.full((1, 256), FORMAT_VERSION, np.float32)
	with open(path, "wb") as f:
		np.save(f, np.vstack([hist.astype(np.float32), marker]), allow_pickle=False)

def load_hist(path):
	"""Load a calibration saved by save_hist. Raises ValueError for pickles and for files
	from the old calibration method (same colours, different meaning)."""
	data = np.load(path, allow_pickle=False)
	if data.shape != (181, 256) or not np.all(data[180] == FORMAT_VERSION):
		raise ValueError("calibration file is from an older version")
	return data[:180].astype(np.float32)

def mask(img, hist, box_x, box_y):
	"""Binary hand mask (uint8 0/255) of the BOX x BOX region at (box_x, box_y)."""
	# Pad the box by the filter reach so edges match a whole-frame computation, then crop.
	pad = 20
	h, w = img.shape[:2]
	x0, y0 = max(box_x - pad, 0), max(box_y - pad, 0)
	x1, y1 = min(box_x + BOX + pad, w), min(box_y + BOX + pad, h)
	hsv = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
	p = hist[hsv[..., 0], hsv[..., 1]]
	p[hsv[..., 2] < V_MIN] = 0
	p = cv2.filter2D(p, -1, DISC)
	p = np.clip(p, 0, 255).astype(np.uint8)
	p = cv2.GaussianBlur(p, (11, 11), 0)
	p = cv2.medianBlur(p, 15)
	m = cv2.threshold(p, THRESH, 255, cv2.THRESH_BINARY)[1]
	return m[box_y - y0:box_y - y0 + BOX, box_x - x0:box_x - x0 + BOX]

def contours(m):
	return cv2.findContours(m.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
