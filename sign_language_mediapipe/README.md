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

A window shows your camera with the hand points drawn.

1. Press a letter or digit key (for example `A`). After a 2-second countdown it records 200 frames
   of that sign (only frames where it sees your hand count). Keep your hand still-ish, but move it
   a little: closer, further, slightly tilted.
2. Repeat for every sign you want. Recording a sign again adds more samples, which helps.
3. `Backspace` deletes the last recording. `Esc` quits. Recordings are saved to
   `data/landmarks.csv` as you go, so you can stop and continue later.

`--samples 300` records more per sign; `--camera 1` picks another webcam.

## 2. Train (seconds)

```bash
python train.py
```

Prints the accuracy on held-out frames and which signs get confused, saves
`results/confusion_matrix.png`, and writes `model.json`. Retrain any time you record more.

## 3. Live on the laptop

```bash
python live.py
```

Show a sign and hold it for 1 second: it is added to the word (the green bar fills up) and spoken.
Take your hand out of view to finish the word and hear it.

Keys: `q` quit, `v` voice on/off, `c` clear, `Backspace` delete the last letter.
Options: `--camera N`, `--no-voice`, `--threshold 0.7` (minimum confidence), `--hold 1.0` (seconds).

## 4. Live on the phone

The phone runs MediaPipe and your model in its own browser; the laptop only serves the files.

```bash
python serve.py
```

1. Phone and laptop on the **same Wi-Fi**. The phone also needs internet (it loads MediaPipe's
   web library from jsDelivr).
2. Open the `https://...:8443` address it prints, in Chrome (Android) or Safari (iPhone).
3. "Connection is not private" -> **Advanced -> Proceed** (the laptop made its own certificate).
4. Tap **Start**, allow the camera. Buttons: Voice, Flip cam, ⌫, Clear.

Retrain on the laptop and just reload the page to use the new model. If the page won't load,
the firewall may be blocking it: `sudo ufw allow 8443/tcp`.

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
