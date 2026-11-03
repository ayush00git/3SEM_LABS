"""Check Code/gestures before training: 50x50 grayscale images, 1200 originals per
class, and class folder ids that match gesture_db.db. Run from Code/."""
import os, sqlite3, sys
from glob import glob
import cv2

def main():
	folders = sorted((d for d in glob("gestures/*") if os.path.isdir(d)), key=lambda d: int(os.path.basename(d)))
	if not folders:
		sys.exit("ERROR: no class folders in Code/gestures/")
	ids = [int(os.path.basename(d)) for d in folders]
	conn = sqlite3.connect("gesture_db.db")
	db = dict(conn.execute("SELECT g_id, g_name FROM gesture").fetchall())
	conn.close()
	problems = []
	total = 0
	for d, cid in zip(folders, ids):
		missing = [n for n in range(1, 1201) if not os.path.exists("%s/%d.jpg" % (d, n))]
		if missing:
			problems.append("class %d: %d of the 1200 originals missing" % (cid, len(missing)))
		for p in glob(d + "/*.jpg"):
			img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
			total += 1
			if img is None or img.shape != (50, 50):
				problems.append("%s: not a 50x50 grayscale image (%s)" % (p, None if img is None else img.shape))
	extra = sorted(set(ids) - set(db))
	absent = sorted(set(db) - set(ids))
	if extra:
		problems.append("folders with no label in gesture_db.db: %s" % extra)
	if absent:
		print("NOTE: labels with no folder (training still works, softmax is sized max id + 1): %s" % absent)
	print("classes: %d, images: %d, ids %d..%d" % (len(ids), total, min(ids), max(ids)))
	if problems:
		print("\n".join(problems[:20]))
		sys.exit("FAILED: %d problem(s)" % len(problems))
	print("OK")

if __name__ == "__main__":
	main()
