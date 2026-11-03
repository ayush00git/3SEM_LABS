"""Shared pieces: MediaPipe hand tracking, the hand-shape features, the classifier,
speech, FPS and drawing. Used by collect.py, train.py and live.py.

The feature recipe in hand_features() is duplicated in web/app.js (handFeatures) for the
phone page. If you change one, change the other: the classifier only works if both match.
"""
import hashlib, json, os, queue, threading, time, urllib.request
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
             "hand_landmarker/float16/1/hand_landmarker.task")
MODEL_SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
MODEL_PATH = os.path.join(ROOT, "models", "hand_landmarker.task")
DATA_CSV = os.path.join(ROOT, "data", "landmarks.csv")
CLASSIFIER_PATH = os.path.join(ROOT, "model.json")
FEATURE_VERSION = "world_v1"
N_FEATURES = 63

# Bones between the 21 MediaPipe hand points, for drawing.
HAND_CONNECTIONS = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
                    (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), (15, 16),
                    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)]


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_landmarker_model():
    """Download MediaPipe's hand model (7.8 MB) on first use and check its SHA-256."""
    if os.path.exists(MODEL_PATH) and _sha256(MODEL_PATH) == MODEL_SHA256:
        return MODEL_PATH
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    print("Downloading MediaPipe hand model (7.8 MB)...")
    tmp = MODEL_PATH + ".part"
    urllib.request.urlretrieve(MODEL_URL, tmp)
    if _sha256(tmp) != MODEL_SHA256:
        os.remove(tmp)
        raise SystemExit("ERROR: downloaded hand model has the wrong checksum. Try again.")
    os.replace(tmp, MODEL_PATH)
    return MODEL_PATH


class Hand:
    """One detected hand: 21 image points (x, y in 0-1, z), 21 world points in metres
    (centred on the hand, independent of image size), and 'Left' or 'Right'."""
    def __init__(self, image_points, world_points, handedness, score):
        self.image_points = image_points
        self.world_points = world_points
        self.handedness = handedness
        self.score = score


class HandTracker:
    """MediaPipe HandLandmarker. mode='video' for webcam streams (uses tracking between
    frames, faster), mode='image' for single photos."""
    def __init__(self, mode="video", min_confidence=0.5):
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions, vision
        self._mp = mp
        running = vision.RunningMode.VIDEO if mode == "video" else vision.RunningMode.IMAGE
        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=ensure_landmarker_model()),
            running_mode=running, num_hands=1,
            min_hand_detection_confidence=min_confidence,
            min_hand_presence_confidence=min_confidence,
            min_tracking_confidence=min_confidence)
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._video = mode == "video"
        self._last_ts = -1
        self._votes = []      # recent (label, score) while the same hand stays in view

    def detect(self, frame_bgr):
        """Return a Hand or None. frame_bgr is an OpenCV BGR image."""
        import cv2
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
        if self._video:
            ts = int(time.monotonic() * 1000)
            ts = max(ts, self._last_ts + 1)          # timestamps must strictly increase
            self._last_ts = ts
            result = self._landmarker.detect_for_video(image, ts)
        else:
            result = self._landmarker.detect(image)
        if not result.hand_landmarks:
            self._votes = []
            return None
        img = np.array([[p.x, p.y, p.z] for p in result.hand_landmarks[0]], np.float32)
        world = np.array([[p.x, p.y, p.z] for p in result.hand_world_landmarks[0]], np.float32)
        cat = result.handedness[0][0]
        handedness = cat.category_name
        if self._video:
            # MediaPipe sometimes flips Left/Right for a frame or two. A flip mirrors the
            # features, so take a score-weighted vote over the last 15 frames instead.
            # web/app.js does the same.
            self._votes = (self._votes + [(handedness, cat.score)])[-15:]
            right = sum(s for h, s in self._votes if h == "Right")
            left = sum(s for h, s in self._votes if h == "Left")
            handedness = "Right" if right >= left else "Left"
        return Hand(img, world, handedness, cat.score)

    def close(self):
        self._landmarker.close()


def hand_features(world_points, handedness):
    """63 numbers describing the hand's shape, the same for any hand position, distance or
    camera. Steps: put the wrist at the origin, mirror left hands so they look like right
    hands, scale so the farthest point is 1 from the wrist, flatten (x, y, z) x 21.
    web/app.js handFeatures() must stay identical."""
    pts = np.asarray(world_points, np.float32).reshape(21, 3)
    pts = pts - pts[0]
    if handedness == "Left":
        pts[:, 0] = -pts[:, 0]
    scale = float(np.max(np.linalg.norm(pts, axis=1)))
    if scale > 0:
        pts = pts / scale
    return pts.reshape(-1)


class Classifier:
    """Small neural network exported by train.py to model.json (plain JSON, no pickle):
    standardise -> dense+ReLU layers -> dense+softmax."""
    def __init__(self, path=CLASSIFIER_PATH):
        if not os.path.exists(path):
            raise SystemExit("ERROR: %s not found. Record signs with collect.py, then run train.py." % path)
        with open(path) as f:
            m = json.load(f)
        if m.get("feature_version") != FEATURE_VERSION:
            raise SystemExit("ERROR: model.json was made with different features. Run train.py again.")
        self.labels = m["labels"]
        self.mean = np.array(m["mean"], np.float32)
        self.std = np.array(m["std"], np.float32)
        self.layers = [(np.array(l["W"], np.float32), np.array(l["b"], np.float32)) for l in m["layers"]]

    def predict_proba(self, features):
        x = (np.asarray(features, np.float32) - self.mean) / self.std
        for i, (W, b) in enumerate(self.layers):
            x = x @ W + b
            if i < len(self.layers) - 1:
                x = np.maximum(x, 0)
        e = np.exp(x - x.max(axis=-1, keepdims=True))
        return e / e.sum(axis=-1, keepdims=True)


class Speaker:
    """One worker thread owns the pyttsx3 engine (it is not thread-safe); callers just
    queue text. If the engine can't start, the app keeps running without voice."""
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
            engine.setProperty("rate", 150)
            self.ok = True
        except Exception as e:
            print("WARNING: could not start the speech engine (%s: %s). Linux: install espeak-ng and alsa-utils."
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
        if self.ok and text:
            try:
                self.q.put_nowait(text)
            except queue.Full:
                pass

    def stop(self):
        if self.ok:
            try:
                self.q.put_nowait(None)
            except queue.Full:
                pass


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


def open_camera(index):
    import cv2
    cam = cv2.VideoCapture(index)
    if not cam.isOpened() or not cam.read()[0]:
        raise SystemExit("ERROR: could not read from camera %d. Try another index with --camera." % index)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cam


def draw_hand(img, hand, color=(0, 255, 0)):
    import cv2
    h, w = img.shape[:2]
    pts = [(int(x * w), int(y * h)) for x, y, _ in hand.image_points]
    for a, b in HAND_CONNECTIONS:
        cv2.line(img, pts[a], pts[b], color, 2)
    for p in pts:
        cv2.circle(img, p, 4, (255, 255, 255), -1)
