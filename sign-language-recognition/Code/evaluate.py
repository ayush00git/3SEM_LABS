import os, pickle
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay

for name in ("cnn_model_keras2.keras", "test_images", "test_labels"):
    if not os.path.exists(name):
        raise SystemExit("ERROR: '%s' not found in %s. Run load_images.py and cnn_model_train.py first "
                         "(from the Code/ folder)." % (name, os.getcwd()))

model = load_model("cnn_model_keras2.keras")

with open("test_images", "rb") as f:
    X = np.array(pickle.load(f))
with open("test_labels", "rb") as f:
    y = np.array(pickle.load(f), dtype=np.int32)

X = X.reshape(X.shape[0], X.shape[1], X.shape[2], 1)

pred = np.argmax(model.predict(X, verbose=0), axis=1)
print("Test accuracy: %.2f%%" % (100 * np.mean(pred == y)))
print(classification_report(y, pred, zero_division=0))

os.makedirs("../img/results", exist_ok=True)
cm = confusion_matrix(y, pred)
fig, ax = plt.subplots(figsize=(14, 14))
ConfusionMatrixDisplay(cm).plot(ax=ax, colorbar=False)
plt.tight_layout()
plt.savefig("../img/results/confusion_matrix.png", dpi=150)
print("Saved ../img/results/confusion_matrix.png")
