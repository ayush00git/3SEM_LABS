import cv2
import os
import pickle
import random
from glob import glob
import numpy as np

# Rotate_images.py writes the mirrored copy of image n as image n + FLIP_OFFSET.
# Both copies must stay in the SAME split, otherwise the model is tested on
# (a mirror of) images it was trained on.
FLIP_OFFSET = 1200
SEED = 42
TRAIN_FRAC, TEST_FRAC = 5/6, 1/12   # validation gets the remaining 1/12


def source_id(path):
	"""Id of the original image: a flipped copy maps back to the image it came from."""
	n = int(os.path.splitext(os.path.basename(path))[0])
	return n - FLIP_OFFSET if n > FLIP_OFFSET else n


def label_of(path):
	return int(os.path.basename(os.path.dirname(path)))


def split_paths(paths, seed=SEED):
	"""Split image paths into train/test/val per class, keeping each original
	image and its mirrored copy together. Returns {"train": [...], "test": [...], "val": [...]}."""
	groups = {}
	for p in paths:
		groups.setdefault((label_of(p), source_id(p)), []).append(p)

	by_label = {}
	for (label, sid) in sorted(groups):
		by_label.setdefault(label, []).append(sid)

	rng = random.Random(seed)
	out = {"train": [], "test": [], "val": []}
	for label in sorted(by_label):
		ids = by_label[label]
		rng.shuffle(ids)
		n = len(ids)
		n_train, n_test = int(TRAIN_FRAC * n), int(TEST_FRAC * n)
		parts = {"train": ids[:n_train], "test": ids[n_train:n_train + n_test], "val": ids[n_train + n_test:]}
		for name, sids in parts.items():
			for sid in sids:
				out[name].extend(groups[(label, sid)])
	return out


def check_no_leakage(splits):
	seen = {}
	for name, paths in splits.items():
		for p in paths:
			key = (label_of(p), source_id(p))
			if seen.setdefault(key, name) != name:
				raise RuntimeError("Leak: %s is in both '%s' and '%s'" % (key, seen[key], name))


def save(name, paths, rng):
	paths = list(paths)
	rng.shuffle(paths)
	images, labels = [], []
	for p in paths:
		images.append(np.array(cv2.imread(p, 0), dtype=np.uint8))
		labels.append(label_of(p))
	print("Length of %s_images" % name, len(images))
	with open(name + "_images", "wb") as f:
		pickle.dump(tuple(images), f)
	with open(name + "_labels", "wb") as f:
		pickle.dump(tuple(labels), f)


if __name__ == "__main__":
	paths = sorted(glob("gestures/*/*.jpg"))
	if not paths:
		raise SystemExit("ERROR: no images found in Code/gestures/<class_id>/*.jpg. "
			"See 'Getting the data and a model' in the README.")
	splits = split_paths(paths)
	check_no_leakage(splits)
	rng = random.Random(SEED)
	for name in ("train", "test", "val"):
		save(name, splits[name], rng)
