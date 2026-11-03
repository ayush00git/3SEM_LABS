# Run guide: fresh clone to live demo

Tested on Linux, CPU only (no GPU, no CUDA). Commands below are for **Fedora**;
Windows notes are at the end. All `python` commands after step 1 run from inside `Code/`.

Based on [Atul-Koundal/sign-language-recognition](https://github.com/Atul-Koundal/sign-language-recognition)
at commit `4f40552`, with the fixes listed in "What was changed" at the bottom.

Reference run (4-core Xeon VM, CPU only): training 15-18 s per epoch, 4 min 20 s for 15 epochs,
~1.9 GB RAM; best val accuracy 99.78%, **test accuracy 99.81%** (17 / 9000 wrong; weakest T 98.0%,
7 98.5%). Three more runs gave 99.53-99.70%. Live-loop processing ~33 ms per frame (~30 FPS ceiling),
measured headless. A laptop CPU may be slower but should stay well under 45 minutes.

A trained `Code/cnn_model_keras2.keras` is included, so you can jump to step 6 (calibrate) and
step 7 (demo) right after step 1. Steps 2-5 rebuild it from scratch.

## 0. System packages (Fedora, needs sudo)

```bash
python3 --version                                # must be 3.12 or 3.13 (see below)
sudo dnf install espeak-ng alsa-utils             # speech engine + aplay, which pyttsx3 uses to play it
```

- `tensorflow==2.21.0` has wheels for Python 3.10-3.13 and `numpy==2.5.4` needs 3.12+,
  so the venv **must be Python 3.12 or 3.13**. If `python3 --version` says 3.14 or newer,
  install 3.12 with `sudo dnf install python3.12` (or use `uv venv --python 3.12 .venv`).
- `alsa-utils` provides `aplay`. Without it the voice engine starts but you hear nothing.
- Optional: `sudo dnf install v4l-utils` and run `v4l2-ctl --list-devices` to find your webcam index.

## 1. Clone and install

```bash
git clone https://github.com/ayush00git/3SEM_LABS.git
cd 3SEM_LABS
git checkout ccr-f57d0005-0nsqgu        # or main, once this branch is merged
cd sign-language-recognition
python3.12 -m venv .venv          # or python3.13, or python3 if it is already 3.12/3.13
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip check
python -c "import tensorflow as tf, cv2; print(tf.__version__, cv2.__version__)"   # 2.21.0 5.0.0
```

A "Could not find cuda drivers" line is normal on CPU.

## 2. Dataset (EvilPort2/Sign-Language 1.0, Zenodo)

Download into its own folder **outside** `Code/`, check the MD5, and copy only the images:

```bash
mkdir -p ../dataset && cd ../dataset
curl -L -o Sign-Language-1.0.zip "https://zenodo.org/records/1244279/files/EvilPort2/Sign-Language-1.0.zip?download=1"
md5sum Sign-Language-1.0.zip      # must be 1225338ccf179518881ba9bb23525f63
unzip -q Sign-Language-1.0.zip -d Sign-Language-1.0
G=$(find "$PWD/Sign-Language-1.0" -type d -name gestures | head -1); echo "$G"
cd ../sign-language-recognition/Code    # i.e. back to this project's Code/ folder
for d in "$G"/*/; do id=$(basename "$d"); mkdir -p "gestures/$id"; cp "$d"/*.jpg "gestures/$id/"; done
python check_dataset.py           # expect: classes: 45, images: 54000, ids 0..44 / OK
```

Do not run any script or model file from the zip; only the `.jpg` files are used.

If Zenodo is unreachable, the same release is git tag `1.0` (commit `f521696e16fd3cc0070c260b4111fb486f188027`):
`git clone --depth 1 --branch 1.0 https://github.com/EvilPort2/Sign-Language ../dataset/Sign-Language-1.0`,
then set `G=../dataset/Sign-Language-1.0/gestures` and copy as above. (There is no zip to MD5 check; git verifies
every file against the commit hash.)

## 3. Preprocess

```bash
python Rotate_images.py > /dev/null     # adds mirrored copies: 1201.jpg-2400.jpg in every class
python check_dataset.py                 # now 108000 images
python load_images.py                   # train 90000 / test 9000 / val 9000; aborts if a leak is found
```

## 4. Train (CPU)

```bash
python -u cnn_model_train.py > train.log 2>&1 &
tail -f train.log                       # Ctrl+C stops tail, not training
```

Writes the best-val_accuracy checkpoint to `cnn_model_keras2.keras`.

## 5. Evaluate

```bash
python evaluate.py                      # test accuracy, per-class report
# confusion matrix: ../img/results/confusion_matrix.png
```

The data comes from one signer, so treat this as an upper bound for your own hand.

## 6. Calibrate your hand histogram (you, at the webcam)

```bash
python set_hand_histogram.py            # add --camera 1 etc. if 0 is not your webcam
```

1. Plain background, even bright light, no skin-coloured things behind you.
2. Hold your hand so it covers **every** small green square on the right.
3. Press `c`. A **Thresh** window opens: you want a clean white hand on black.
   If it is noisy or patchy, move or re-light and press `c` again.
4. Press `s` to save `hist` (pressing `s` before `c` just reminds you to capture first).
   `q` quits without saving.

`hist` is saved as a plain numpy array. Old pickled `hist` files are refused, never loaded.

## 7. Live demo

```bash
python final.py                         # --camera N to pick a webcam, --no-voice to start muted
```

Put your hand inside the green 300x300 box. Text appears above 70% confidence; holding a sign
steady adds it to the word, and removing your hand speaks the word. FPS is shown top-left.

Keys: `q` quit, `v` voice on/off, `t` calculator mode, `c` back to text mode.

Calculator mode: sign digits for the first number, hold "Best of Luck" to confirm, sign a digit
for the operator (1 `+`, 2 `-`, 3 `*`, 4 `/`, 5 `%`, 6 `**`, 7 `>>`, 8 `<<`, 9 `&`, 0 `|`),
then the second number and "Best of Luck" again to compute. Sign "C" to clear.

### Wayland (Fedora GNOME)

If no OpenCV windows appear, or you see a Qt "wayland" plugin warning, run through XWayland:

```bash
QT_QPA_PLATFORM=xcb python set_hand_histogram.py
QT_QPA_PLATFORM=xcb python final.py
```

### Troubleshooting

- `could not read from camera 0`: try `--camera 1`, close other apps using the camera, check `ls /dev/video*`.
- Hand not detected / random letters: recalibrate (step 6) in the same light you demo in.
- No sound: `sudo dnf install espeak-ng alsa-utils`; the app prints a warning and keeps running without voice if the engine fails.

## Windows notes

- Install Python 3.12 or 3.13 from python.org, then in PowerShell:
  ```powershell
  py -3.12 -m venv .venv
  .venv\Scripts\Activate.ps1      # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  pip install -r requirements.txt
  ```
- Speech uses Windows SAPI5 voices; no espeak or alsa-utils needed.
- Download and check: `curl.exe -L -o Sign-Language-1.0.zip "<same URL>"`, then
  `certutil -hashfile Sign-Language-1.0.zip MD5`, then `Expand-Archive Sign-Language-1.0.zip ..\dataset\Sign-Language-1.0`.
- Copy images (PowerShell, from `Code\`):
  ```powershell
  $G = (Get-ChildItem ..\..\dataset\Sign-Language-1.0 -Recurse -Directory -Filter gestures | Select-Object -First 1).FullName
  Get-ChildItem $G -Directory | ForEach-Object { New-Item -ItemType Directory -Force "gestures\$($_.Name)" | Out-Null; Copy-Item "$($_.FullName)\*.jpg" "gestures\$($_.Name)\" }
  ```
- `python Rotate_images.py > $null`; run training in a second window instead of `&`:
  `python -u cnn_model_train.py *> train.log`, and watch it with `Get-Content train.log -Wait`.
- Webcam indexes can differ from Linux (built-in camera is usually 0). If the camera is slow to open,
  that is the Media Foundation backend; it still works.
- No Wayland/`QT_QPA_PLATFORM` step on Windows.
- A model trained on Fedora (`cnn_model_keras2.keras`) works on Windows unchanged; `hist` should be
  re-calibrated on the camera and lighting you use.

## What was changed (vs upstream `4f40552`)

- `cnn_model_train.py`: softmax size and one-hot encoding both use max class id + 1, so a missing class folder can't make them disagree.
- `cnn_model_train.py`: a `Rescaling(1/255)` first layer (no weights; conv/dense layers unchanged). On raw 0-255 pixels, training was a
  coin flip: one run reached 99.9%, the next stalled at 7.7% val accuracy. With rescaling, 4 of 4 runs reached 99.5-99.8% test accuracy.
  It is inside the saved model, so `evaluate.py` and `final.py` still feed raw pixels.
- `set_hand_histogram.py`: `--camera` (default 0, was "try 1 then 0"); checks every `cam.read()`; `s` before `c` no longer crashes; `q` quits; saves `hist` as a plain numpy array, not a pickle.
- Bundled `Code/hist` deleted: it was a pickle from another machine (unsafe to load) and tuned to someone else's skin and lighting.
- `final.py`:
  - `--camera` and `--no-voice` options; every `cam.read()` is checked, and the app exits cleanly if the camera fails.
  - The model is called directly (`model(x, training=False)`, compiled once with `tf.function`), not with `model.predict()`: about 2 ms per frame instead of about 75 ms.
  - FPS counter drawn on the video.
  - All speech goes through one worker thread and a bounded queue. Before, it started a thread per phrase and busy-waited on `engine._inLoop`. If the engine fails to start, the app prints a warning and runs silently.
  - `eval()` in calculator mode replaced by `safe_calc()`, which only accepts `<digits><op><digits>` with the mode's ten operators. Huge powers and shifts are refused, and divide by zero shows "Invalid operation".
  - Labels are read from `gesture_db.db` once at startup, not once per frame.
  - Mode keys now match the docs: `t` calculator, `c` text. The code had them the other way round.
- `create_gestures.py`: `--camera`, read checks, `q` to stop, numpy `hist`, parameterized SQL.
- New `check_dataset.py`: verifies image size, counts and ids against `gesture_db.db`.
