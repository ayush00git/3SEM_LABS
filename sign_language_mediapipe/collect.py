"""Record your own signs into data/landmarks.csv for train.py.

Usage:
    python collect.py [--camera N] [--samples 200]

Keys (in the camera window):
    A-Z, 0-9    record that sign: 2-second countdown, then --samples frames with a hand
    BACKSPACE   undo: delete the last recorded session from the file
    ESC         quit

Each recording run is one "session" (a number that goes up by 1). Rows are
label,session,frame,f0..f62 where f0..f62 come from common.hand_features().
"""
import argparse, csv, os, string, time
import cv2
import common
from common import HandTracker, hand_features, open_camera, draw_hand, FPS, N_FEATURES

HEADER = ["label", "session", "frame"] + ["f%d" % i for i in range(N_FEATURES)]
COUNTDOWN = 2.0                                   # seconds before recording starts
KEYS = {ord(c): c for c in string.ascii_uppercase + string.digits}
KEYS.update({ord(c.lower()): c for c in string.ascii_uppercase})
BACKSPACE = (8, 127)
ESC = 27
WINDOW = "collect - sign language"


def read_rows(path):
    """All data rows of the CSV (without header), or [] if the file doesn't exist."""
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)                        # skip header
        return [r for r in reader if r]


def summary(rows):
    """Compact 'A:200 B:200 L:400' count of samples per label."""
    counts = {}
    for r in rows:
        counts[r[0]] = counts.get(r[0], 0) + 1
    return " ".join("%s:%d" % (k, counts[k]) for k in sorted(counts)) or "(no samples yet)"


def next_session(rows):
    return max((int(r[1]) for r in rows), default=0) + 1


def append_session(path, rows):
    """Append one session's rows, writing the header if the file is new, and flush."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    new_file = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(HEADER)
        writer.writerows(rows)
        f.flush()
        os.fsync(f.fileno())


def undo_last_session(path):
    """Delete all rows of the highest session number. Returns (session, label, n) or None."""
    rows = read_rows(path)
    if not rows:
        return None
    last = max(int(r[1]) for r in rows)
    removed = [r for r in rows if int(r[1]) == last]
    kept = [r for r in rows if int(r[1]) != last]
    tmp = path + ".tmp"                           # rewrite via temp file so a crash can't wipe the data
    with open(tmp, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(kept)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    return last, removed[0][0], len(removed)


def put_text(img, text, y, color=(255, 255, 255), scale=0.6):
    # Black outline first so the text is readable on any background.
    cv2.putText(img, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)


def main():
    ap = argparse.ArgumentParser(description="Record hand signs into a CSV for train.py.")
    ap.add_argument("--camera", type=int, default=0, help="webcam index (default 0)")
    ap.add_argument("--samples", type=int, default=200, help="frames with a hand per recording (default 200)")
    ap.add_argument("--data", default=common.DATA_CSV, help=argparse.SUPPRESS)  # for tests
    args = ap.parse_args()
    if args.samples < 1:
        raise SystemExit("ERROR: --samples must be at least 1.")
    path = args.data

    rows = read_rows(path)
    print("Data file: %s" % path)
    print("Samples per label: %s" % summary(rows))
    print("Press A-Z / 0-9 to record a sign, BACKSPACE to undo the last recording, ESC to quit.")

    cam = open_camera(args.camera)
    tracker = HandTracker(mode="video")
    fps = FPS()
    label = None              # sign being recorded (None = idle)
    start = 0.0               # when the countdown started
    recorded = []             # rows of the session in progress
    session = 0
    try:
        while True:
            ok, frame = cam.read()
            if not ok or frame is None:
                print("Camera stopped returning frames; exiting.")
                break
            frame = cv2.flip(frame, 1)            # selfie view
            hand = tracker.detect(frame)
            if hand is not None:
                draw_hand(frame, hand)
            h, w = frame.shape[:2]

            # Countdown, then record frames that contain a hand.
            if label is not None:
                left = COUNTDOWN - (time.monotonic() - start)
                if left > 0:
                    put_text(frame, "Get ready: %s  %d" % (label, int(left) + 1), h // 2, (0, 255, 255), 1.2)
                else:
                    if hand is not None:
                        feats = hand_features(hand.world_points, hand.handedness)
                        recorded.append([label, session, len(recorded)] + ["%.6f" % v for v in feats])
                    done = len(recorded) / args.samples
                    cv2.rectangle(frame, (10, h - 40), (w - 10, h - 20), (255, 255, 255), 1)
                    cv2.rectangle(frame, (10, h - 40), (10 + int((w - 20) * done), h - 20), (0, 200, 0), -1)
                    put_text(frame, "Recording %s: %d/%d" % (label, len(recorded), args.samples), h - 50, (0, 0, 255))
                    put_text(frame, "Move your hand a little: closer, further, tilt", h - 75, (0, 255, 255))
                    if len(recorded) >= args.samples:
                        append_session(path, recorded)
                        rows += recorded
                        print("Saved session %d: %d samples of %s" % (session, len(recorded), label))
                        print("Samples per label: %s" % summary(rows))
                        label, recorded = None, []

            # Status lines at the top.
            if hand is not None:
                put_text(frame, "Hand: yes (%s)" % hand.handedness, 25, (0, 255, 0))
            else:
                put_text(frame, "Hand: NO", 25, (0, 0, 255))
            put_text(frame, "Recording: %s" % (label or "-"), 50)
            put_text(frame, summary(rows), 75, scale=0.5)
            put_text(frame, "A-Z/0-9 record  BACKSPACE undo  ESC quit  %.0f fps" % fps.tick(), 100, scale=0.45)
            cv2.imshow(WINDOW, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ESC:
                if label is not None:
                    print("Recording of %s cancelled (not saved)." % label)
                break
            if label is not None:
                continue                          # ignore other keys while busy
            if key in KEYS:
                label, start, recorded = KEYS[key], time.monotonic(), []
                session = next_session(rows)
                print("Recording %s (session %d)..." % (label, session))
            elif key in BACKSPACE:
                undone = undo_last_session(path)
                if undone is None:
                    print("Nothing to undo.")
                else:
                    print("Undo: removed session %d (%d samples of %s)" % (undone[0], undone[2], undone[1]))
                    rows = read_rows(path)
                    print("Samples per label: %s" % summary(rows))
    finally:
        cam.release()
        cv2.destroyAllWindows()
        tracker.close()


if __name__ == "__main__":
    main()
