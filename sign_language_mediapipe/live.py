"""Live sign language recognition from the webcam, using MediaPipe hand landmarks.

Show a sign and hold it: after --hold seconds it is added to the current word and spoken
(keep holding to repeat it). Take your hand away for 0.8 s to finish the word: it is
spoken and moved into the sentence. 1-character labels (A, B, ...) spell words letter by
letter; longer labels (HELLO, THANKS, ...) are added as whole words.

Usage:
    python live.py [--camera N] [--model model.json] [--no-voice] [--threshold 0.7] [--hold 1.0]

Keys (click the window first):
    q          quit
    v          voice on/off
    c          clear the word and the sentence
    BACKSPACE  delete the last character of the word

The word-building rules in WordBuilder are duplicated in the phone page (web/app.js).
If you change one, change the other.
"""
import argparse, time
from collections import deque

import cv2
import numpy as np

from common import (CLASSIFIER_PATH, FPS, Classifier, HandTracker, Speaker, draw_hand,
                    hand_features, open_camera)

WINDOW = "Sign Language (MediaPipe)"
SMOOTH_FRAMES = 5       # average the probabilities of the last 5 frames with a hand
NO_HAND_GAP = 0.8       # seconds without a hand that finish the word
SENTENCE_WORDS = 8      # keep the last 8 words
PANEL_W = 420


class WordBuilder:
    """Turns per-frame probabilities into letters, words and a sentence.

    update(probs, now) takes the classifier's probabilities for this frame (or None if
    there is no hand) and the time in seconds, and returns a list of events:
    ("add", label) when a sign is appended and ("word", word) when a word is finished.
    """
    def __init__(self, labels, threshold=0.7, hold=1.0):
        self.labels = list(labels)
        self.threshold = threshold
        self.hold = hold
        self.buffer = deque(maxlen=SMOOTH_FRAMES)
        self.word = ""
        self.sentence = []
        self.avg = None              # averaged probabilities (None without a hand)
        self.label, self.conf = None, 0.0
        self.candidate = None        # label being held, or None ("unsure"/no hand)
        self.hold_start = None
        self.last_hand = None        # time a hand was last seen

    def update(self, probs, now):
        events = []
        if probs is None:
            self.buffer.clear()
            self.avg, self.label, self.conf = None, None, 0.0
            candidate = None
            # Hand gone long enough: finish the word.
            if self.last_hand is not None and now - self.last_hand >= NO_HAND_GAP and self.word:
                events.append(("word", self.word.strip()))
                self.sentence.append(self.word.strip())
                self.sentence = self.sentence[-SENTENCE_WORDS:]
                self.word = ""
        else:
            self.last_hand = now
            self.buffer.append(np.asarray(probs, np.float32))
            self.avg = np.mean(self.buffer, axis=0)
            i = int(np.argmax(self.avg))
            self.label, self.conf = self.labels[i], float(self.avg[i])
            candidate = self.label if self.conf >= self.threshold else None

        # Candidate changed: restart its hold timer.
        if candidate != self.candidate:
            self.candidate = candidate
            self.hold_start = now if candidate is not None else None
        elif candidate is not None and now - self.hold_start >= self.hold:
            self.append(candidate)
            events.append(("add", candidate))
            self.hold_start = now     # holding longer repeats it
        return events

    def append(self, label):
        if len(label) == 1:
            self.word += label
        else:
            self.word += ("" if self.word == "" or self.word.endswith(" ") else " ") + label + " "

    def progress(self, now):
        """0-1: how far the current candidate is towards being appended."""
        if self.candidate is None:
            return 0.0
        return min(1.0, (now - self.hold_start) / self.hold) if self.hold > 0 else 1.0

    def top(self, n=3):
        if self.avg is None:
            return []
        order = np.argsort(self.avg)[::-1][:n]
        return [(self.labels[i], float(self.avg[i])) for i in order]

    def backspace(self):
        self.word = self.word[:-1]

    def clear(self):
        self.word = ""
        self.sentence = []


def wrap(text, width, scale, thick=1, font=cv2.FONT_HERSHEY_SIMPLEX):
    """Split text into lines that fit `width` pixels (long words are cut)."""
    lines, line = [], ""
    for w in text.split():
        while cv2.getTextSize(w, font, scale, thick)[0][0] > width and len(w) > 1:
            k = len(w) - 1
            while k > 1 and cv2.getTextSize(w[:k], font, scale, thick)[0][0] > width:
                k -= 1
            if line:
                lines.append(line)
                line = ""
            lines.append(w[:k])
            w = w[k:]
        test = (line + " " + w).strip()
        if cv2.getTextSize(test, font, scale, thick)[0][0] <= width:
            line = test
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def put(img, text, org, scale=0.6, color=(230, 230, 230), thick=1):
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)


def draw_panel(height, wb, now, hand_seen, voice):
    panel = np.full((height, PANEL_W, 3), 30, np.uint8)
    x, inner = 15, PANEL_W - 30
    # Prediction, big.
    if not hand_seen:
        put(panel, "show your hand", (x, 50), 0.9, (150, 150, 150), 2)
    elif wb.candidate is None:
        put(panel, "unsure", (x, 50), 1.1, (0, 165, 255), 2)
        put(panel, "(%s %d%%)" % (wb.label, round(wb.conf * 100)), (x, 80), 0.6, (150, 150, 150))
    else:
        big = wrap(wb.candidate, inner, 1.6, 3)[0]
        put(panel, big, (x, 60), 1.6, (0, 255, 0), 3)
        put(panel, "%d%%" % round(wb.conf * 100), (x, 88), 0.6, (180, 255, 180))
    # Top 3 with bars.
    y = 120
    for label, p in wb.top(3):
        cv2.rectangle(panel, (x + 110, y - 12), (x + 110 + int(p * (inner - 170)), y), (90, 140, 90), -1)
        put(panel, label[:9], (x, y), 0.55)
        put(panel, "%3d%%" % round(p * 100), (PANEL_W - 60, y), 0.55)
        y += 24
    # Word (last lines that fit) and sentence (newest words kept).
    y = 210
    put(panel, "Word:", (x, y), 0.55, (150, 150, 150))
    for line in (wrap(wb.word, inner, 0.9, 2) or [""])[-2:]:
        y += 32
        put(panel, line, (x, y), 0.9, (255, 255, 255), 2)
    y += 35
    put(panel, "Sentence:", (x, y), 0.55, (150, 150, 150))
    help_top = height - 75
    max_lines = max(1, (help_top - y - 15) // 26)
    lines = wrap(" ".join(wb.sentence), inner, 0.65, 1)
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
    for line in lines:
        y += 26
        put(panel, line, (x, y), 0.65, (255, 255, 200))
    # Voice + key help.
    put(panel, "Voice: " + ("ON" if voice else "OFF"), (x, height - 55), 0.55,
        (0, 255, 0) if voice else (0, 0, 255))
    put(panel, "q quit  v voice  c clear", (x, height - 32), 0.5, (150, 150, 150))
    put(panel, "BACKSPACE delete letter", (x, height - 12), 0.5, (150, 150, 150))
    return panel


def main():
    ap = argparse.ArgumentParser(description="Live sign language recognition (MediaPipe).")
    ap.add_argument("--camera", type=int, default=0, help="camera index (default 0)")
    ap.add_argument("--model", default=CLASSIFIER_PATH, help="classifier made by train.py")
    ap.add_argument("--no-voice", action="store_true", help="start with voice off")
    ap.add_argument("--threshold", type=float, default=0.7, help="minimum confidence (0-1)")
    ap.add_argument("--hold", type=float, default=1.0, help="seconds to hold a sign")
    args = ap.parse_args()

    clf = Classifier(args.model)
    wb = WordBuilder(clf.labels, args.threshold, args.hold)
    cam = open_camera(args.camera)
    tracker = HandTracker(mode="video")
    speaker = Speaker()
    voice = not args.no_voice
    fps = FPS()
    print("Running. Press q in the window to quit.")
    try:
        while True:
            ok, frame = cam.read()
            if not ok or frame is None:
                print("ERROR: lost the camera (could not read a frame). Exiting.")
                break
            frame = cv2.flip(frame, 1)
            now = time.monotonic()
            hand = tracker.detect(frame)
            probs = clf.predict_proba(hand_features(hand.world_points, hand.handedness)) if hand else None
            for kind, text in wb.update(probs, now):
                if voice:
                    speaker.say(text)

            # Camera view: hand, FPS, hold progress bar.
            view = frame.copy()
            if hand:
                draw_hand(view, hand)
            put(view, "FPS %.0f" % fps.tick(), (10, 28), 0.8, (0, 255, 255), 2)
            h, w = view.shape[:2]
            cv2.rectangle(view, (10, h - 25), (w - 10, h - 10), (60, 60, 60), -1)
            p = wb.progress(now)
            if p > 0:
                cv2.rectangle(view, (10, h - 25), (10 + int(p * (w - 20)), h - 10), (0, 255, 0), -1)
            cv2.imshow(WINDOW, np.hstack([view, draw_panel(h, wb, now, hand is not None, voice)]))

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("v"):
                voice = not voice
            elif key == ord("c"):
                wb.clear()
            elif key in (8, 127):
                wb.backspace()
    except KeyboardInterrupt:
        pass
    finally:
        cam.release()
        cv2.destroyAllWindows()
        speaker.stop()
        tracker.close()


if __name__ == "__main__":
    main()
