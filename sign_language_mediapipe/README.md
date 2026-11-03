# Sign language recognition with MediaPipe

Real-time recognition of static hand signs from a webcam or a phone camera. No calibration,
no plain-background rule: [MediaPipe Hands](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)
finds 21 points on your hand (fingertips, knuckles, wrist) in any light or background, and a small
neural network trained on **your own** recordings turns those points into a sign. Runs on a CPU.

```
webcam/phone camera -> MediaPipe (21 hand points) -> 63 shape numbers -> small neural net -> sign -> word -> speech
```

## Setup (Ubuntu, once)

```bash
sudo apt install python3-venv espeak-ng alsa-utils libegl1   # libegl1 is already there on desktop Ubuntu
git clone https://github.com/ayush00git/3SEM_LABS.git
cd 3SEM_LABS
git checkout sign-language-mediapipe        # or master once this is merged
cd sign_language_mediapipe
python3 -m venv .venv                        # Python 3.12 or 3.13
source .venv/bin/activate
pip install -r requirements.txt
```

Fedora: `sudo dnf install espeak-ng alsa-utils mesa-libEGL`. Windows: `py -3.12 -m venv .venv`,
`.venv\Scripts\activate`, `pip install -r requirements.txt` (speech uses Windows voices).

The first run downloads MediaPipe's hand model (7.8 MB) into `models/` and checks its checksum.

Every new terminal: `cd 3SEM_LABS/sign_language_mediapipe && source .venv/bin/activate`.

## 1. Record your signs (about 10-15 minutes for the alphabet)

```bash
python collect.py
```

__COLLECT__

## 2. Train (seconds)

```bash
python train.py
```

__TRAIN__

## 3. Live on the laptop

```bash
python live.py
```

__LIVE__

## 4. Live on the phone

The phone runs MediaPipe and your model in its own browser; the laptop only serves the files.

```bash
python serve.py
```

__PHONE__

## Tips

- Record each sign with small variations (closer, further, slightly tilted), and record a second
  session later in different light: that is what makes it reliable.
- Signs that look different as a hand *shape* work best. Moving signs (J, Z) are recorded as a
  still pose.
- If two signs keep getting mixed up, the confusion matrix in `results/` shows which; record more
  samples of both.
- If OpenCV windows don't appear under Wayland, run with `QT_QPA_PLATFORM=xcb python live.py`.

## Files

| File | What it does |
|---|---|
| `common.py` | MediaPipe hand tracking, the shape features, the classifier, speech, drawing |
| `collect.py` | records your signs into `data/landmarks.csv` |
| `train.py` | trains the network, writes `model.json` and `results/confusion_matrix.png` |
| `live.py` | real-time recognition on the laptop webcam |
| `serve.py` + `web/` | phone version (runs in the phone's browser) |

`data/`, `model.json`, `models/` and `certs/` are created locally and not committed.
