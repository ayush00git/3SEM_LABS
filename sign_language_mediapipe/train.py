"""Train the sign classifier on recorded hand landmarks and export it to model.json.

Usage:
    python train.py [--data data/landmarks.csv] [--out model.json]

Reads the CSV written by collect.py (label, session, frame, f0..f62), holds out the last
20% of frames of every session as a test set (consecutive frames are near-duplicates, so
a random split would flatter the model), trains a small neural network and saves it as
plain JSON (no pickle). live.py and the phone page both read that model.json.
"""
import argparse, csv, datetime, json, os, sys, time
from collections import Counter

import numpy as np

import common

MIN_SAMPLES = 30          # labels with fewer rows are dropped
TEST_FRACTION = 0.2       # last 20% of each session's frames
GOOD_ACCURACY = 0.90
RESULTS_DIR = os.path.join(common.ROOT, "results")
EXPECTED_HEADER = ["label", "session", "frame"] + ["f%d" % i for i in range(common.N_FEATURES)]


def fail(msg):
    raise SystemExit("ERROR: " + msg)


def load_csv(path):
    """Return labels, sessions, frames, features (n x 63) from the landmarks CSV."""
    if not os.path.exists(path):
        fail("%s not found. Record signs first: python collect.py" % path)
    labels, sessions, frames, feats = [], [], [], []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            fail("%s is empty. Record signs first: python collect.py" % path)
        header = [h.strip() for h in header]
        if header != EXPECTED_HEADER:
            fail("%s has an unexpected header (wanted label,session,frame,f0..f%d; got %s...). "
                 "It may be from an old version; record signs again: python collect.py"
                 % (path, common.N_FEATURES - 1, ",".join(header[:5])))
        for n, row in enumerate(reader, start=2):
            if not row:
                continue
            if len(row) != len(EXPECTED_HEADER):
                print("WARNING: skipping line %d (%d columns instead of %d)" % (n, len(row), len(EXPECTED_HEADER)))
                continue
            try:
                x = [float(v) for v in row[3:]]
                fr = int(float(row[2]))
            except ValueError:
                print("WARNING: skipping line %d (not a number)" % n)
                continue
            labels.append(row[0].strip())
            sessions.append(row[1].strip())
            frames.append(fr)
            feats.append(x)
    if not labels:
        fail("%s has no samples. Record signs first: python collect.py" % path)
    X = np.array(feats, np.float64)
    if not np.all(np.isfinite(X)):
        keep = np.all(np.isfinite(X), axis=1)
        print("WARNING: dropping %d rows with NaN/inf values" % int((~keep).sum()))
        X = X[keep]
        labels = [l for l, k in zip(labels, keep) if k]
        sessions = [s for s, k in zip(sessions, keep) if k]
        frames = [fr for fr, k in zip(frames, keep) if k]
    return np.array(labels, dtype=object), np.array(sessions, dtype=object), np.array(frames), X


def drop_small_labels(y, sess, frames, X):
    counts = Counter(y)
    small = sorted(l for l, c in counts.items() if c < MIN_SAMPLES)
    for l in small:
        print("WARNING: dropping '%s' (only %d samples, need %d). Record more with collect.py."
              % (l, counts[l], MIN_SAMPLES))
    keep = np.array([l not in small for l in y])
    y, sess, frames, X = y[keep], sess[keep], frames[keep], X[keep]
    if len(set(y)) < 2:
        fail("need at least 2 signs with %d+ samples each (have: %s). Record more: python collect.py"
             % (MIN_SAMPLES, ", ".join("%s=%d" % kv for kv in sorted(counts.items())) or "none"))
    return y, sess, frames, X


def split_by_time(y, sess, frames):
    """Boolean test mask: the last 20% of frames in each (label, session) group."""
    test = np.zeros(len(y), bool)
    groups = {}
    for i, key in enumerate(zip(y, sess)):
        groups.setdefault(key, []).append(i)
    for idx in groups.values():
        idx = np.array(idx)[np.argsort(frames[idx], kind="stable")]
        n_test = int(round(len(idx) * TEST_FRACTION))
        if len(idx) >= 5:
            n_test = max(1, n_test)
        if n_test:
            test[idx[-n_test:]] = True
    return test


def rotate_z(X, rng, max_deg=12.0):
    """Rotate each hand about z by a random angle, keep wrist at origin, rescale to 1."""
    pts = X.reshape(-1, 21, 3).copy()
    a = np.radians(rng.uniform(-max_deg, max_deg, len(pts)))
    c, s = np.cos(a)[:, None], np.sin(a)[:, None]
    x, y = pts[:, :, 0].copy(), pts[:, :, 1].copy()
    pts[:, :, 0] = c * x - s * y
    pts[:, :, 1] = s * x + c * y
    pts -= pts[:, :1, :]
    scale = np.linalg.norm(pts, axis=2).max(axis=1)
    scale[scale == 0] = 1.0
    pts /= scale[:, None, None]
    return pts.reshape(len(X), -1)


def augment(X, y, rng):
    """Original + 2 noisy copies + 2 slightly rotated copies."""
    parts = [X]
    for _ in range(2):
        parts.append(X + rng.normal(0, 0.01, X.shape))
    for _ in range(2):
        parts.append(rotate_z(X, rng))
    return np.vstack(parts), np.concatenate([y] * len(parts))


def r7(a):
    """Round floats to 7 significant digits (nested lists) to keep model.json small."""
    return np.vectorize(lambda v: float("%.7g" % v), otypes=[float])(np.asarray(a, np.float64)).tolist()


def export_model(path, clf, mean, std, acc, n_train, n_test):
    model = {
        "feature_version": common.FEATURE_VERSION,
        "labels": [str(l) for l in clf.classes_],
        "mean": r7(mean),
        "std": r7(std),
        "layers": [{"W": r7(W), "b": r7(b)} for W, b in zip(clf.coefs_, clf.intercepts_)],
        "test_accuracy": round(float(acc), 6),
        "n_train": int(n_train),
        "n_test": int(n_test),
        "created": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "w") as f:
        json.dump(model, f, separators=(",", ":"))
    os.replace(tmp, path)


def save_confusion(cm, labels, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = len(labels)
    size = max(5.0, 0.45 * n + 2)
    fig, ax = plt.subplots(figsize=(size + 1, size))
    rows = cm.sum(axis=1, keepdims=True)
    frac = cm / np.maximum(rows, 1)
    im = ax.imshow(frac, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45 if n > 8 else 0, ha="right" if n > 8 else "center")
    ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion matrix (test set; colour = share of true sign)")
    fs = 9 if n <= 15 else 7 if n <= 30 else 5
    for i in range(n):
        for j in range(n):
            if cm[i, j]:
                ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=fs,
                        color="white" if frac[i, j] > 0.5 else "black")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description="Train the sign classifier and export model.json.")
    ap.add_argument("--data", default=common.DATA_CSV, help="landmarks CSV (default: data/landmarks.csv)")
    ap.add_argument("--out", default=common.CLASSIFIER_PATH, help="output model (default: model.json)")
    ap.add_argument("--results", default=RESULTS_DIR, help="folder for confusion_matrix.png")
    args = ap.parse_args()
    t0 = time.perf_counter()

    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler

    y, sess, frames, X = load_csv(args.data)
    print("Loaded %d samples, %d signs from %s" % (len(y), len(set(y)), args.data))
    y, sess, frames, X = drop_small_labels(y, sess, frames, X)

    # Split: last 20% of frames of each session is the test set.
    test = split_by_time(y, sess, frames)
    Xtr, ytr, Xte, yte = X[~test], y[~test], X[test], y[test]
    print("Split (last %d%% of each session held out): %d train, %d test"
          % (TEST_FRACTION * 100, len(ytr), len(yte)))
    for l in sorted(set(y)):
        n_sess = len(set(sess[y == l]))
        print("  %-16s train %5d  test %4d  sessions %d" % (l, (ytr == l).sum(), (yte == l).sum(), n_sess))
    if len(yte) == 0:
        fail("test set is empty; record more frames per sign.")

    # Augment train set only, then standardise.
    rng = np.random.default_rng(42)
    Xaug, yaug = augment(Xtr, ytr, rng)
    scaler = StandardScaler().fit(Xaug)
    mean = scaler.mean_
    std = scaler.scale_.copy()
    std[std < 1e-6] = 1.0
    Xaug_s = (Xaug - mean) / std
    Xte_s = (Xte - mean) / std

    print("Training on %d rows (with augmentation)..." % len(yaug))
    # No early stopping: with a few hundred samples per sign it stops after ~12 epochs with
    # soft probabilities, and live.py then rarely reaches its 0.7 confidence threshold.
    # Training runs until the loss stops improving (sklearn's tol), still only seconds.
    clf = MLPClassifier(hidden_layer_sizes=(128, 64), activation="relu", alpha=1e-4,
                        max_iter=300, early_stopping=False, random_state=42)
    t1 = time.perf_counter()
    clf.fit(Xaug_s, yaug)
    print("Trained in %.1f s (%d epochs)" % (time.perf_counter() - t1, clf.n_iter_))

    # Evaluate.
    pred = clf.predict(Xte_s)
    acc = accuracy_score(yte, pred)
    labels = [str(l) for l in clf.classes_]
    print("\nTest accuracy: %.1f%% (%d/%d)\n" % (acc * 100, int((pred == yte).sum()), len(yte)))
    print(classification_report(yte, pred, labels=clf.classes_, target_names=labels, zero_division=0))
    cm = confusion_matrix(yte, pred, labels=clf.classes_)
    pairs = sorted(((cm[i, j], labels[i], labels[j]) for i in range(len(labels))
                    for j in range(len(labels)) if i != j and cm[i, j]), reverse=True)
    if pairs:
        print("Most confused (true -> predicted):")
        for c, a, b in pairs[:5]:
            print("  %-16s -> %-16s %d" % (a, b, c))
    else:
        print("No confusions on the test set.")
    cm_path = os.path.join(args.results, "confusion_matrix.png")
    save_confusion(cm, labels, cm_path)
    print("Confusion matrix saved to %s" % cm_path)

    # Export and check the JSON model gives the same answers as sklearn.
    export_model(args.out, clf, mean, std, acc, len(ytr), len(yte))
    loaded = common.Classifier(args.out)
    js_pred = np.array([loaded.labels[int(np.argmax(loaded.predict_proba(x)))] for x in Xte])
    mismatch = int((js_pred != pred.astype(str)).sum())
    assert mismatch == 0, "exported model disagrees with sklearn on %d test samples" % mismatch

    print("\nModel saved to %s (%d signs, checked against sklearn) in %.1f s total."
          % (args.out, len(labels), time.perf_counter() - t0))
    if acc < GOOD_ACCURACY:
        print("\nAccuracy is below %d%%. Tips:" % (GOOD_ACCURACY * 100))
        print("  - Record more varied samples: move the hand around, tilt it a little, vary distance.")
        print("  - Record a second session for each sign (another time, light or place).")
        print("  - Look at the most-confused pairs above: those signs may look alike to the camera;")
        print("    make them more distinct or record them more carefully.")
    print("Run: python live.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
