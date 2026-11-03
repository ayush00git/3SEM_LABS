import numpy as np
import pickle
import cv2, os
from glob import glob
from tensorflow.keras import optimizers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def get_image_size():
	# Use the first image found, so this does not depend on a specific class folder existing.
	paths = sorted(glob('gestures/*/*.jpg'))
	if not paths:
		raise SystemExit("ERROR: no images found in Code/gestures/<class_id>/*.jpg. Get the dataset "
			"(Zenodo, see README) or record your own with create_gestures.py, then run "
			"Rotate_images.py and load_images.py before training.")
	return cv2.imread(paths[0], 0).shape

def get_num_of_classes():
	# Size the softmax as max label + 1, the same rule to_categorical uses, so a
	# missing class folder cannot make the two disagree.
	ids = [int(os.path.basename(d)) for d in glob('gestures/*') if os.path.basename(d).isdigit()]
	return max(ids) + 1

image_x, image_y = get_image_size()

def cnn_model():
	num_of_classes = get_num_of_classes()
	model = Sequential()
	model.add(Conv2D(16, (2,2), input_shape=(image_x, image_y, 1), activation='relu'))
	model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same'))
	model.add(Conv2D(32, (3,3), activation='relu'))
	model.add(MaxPooling2D(pool_size=(3, 3), strides=(3, 3), padding='same'))
	model.add(Conv2D(64, (5,5), activation='relu'))
	model.add(MaxPooling2D(pool_size=(5, 5), strides=(5, 5), padding='same'))
	model.add(Flatten())
	model.add(Dense(128, activation='relu'))
	model.add(Dropout(0.2))
	model.add(Dense(num_of_classes, activation='softmax'))
	sgd = optimizers.SGD(learning_rate=1e-2)
	model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
	filepath="cnn_model_keras2.keras"
	checkpoint1 = ModelCheckpoint(filepath, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')
	callbacks_list = [checkpoint1]
	#from keras.utils import plot_model
	#plot_model(model, to_file='model.png', show_shapes=True)
	return model, callbacks_list

def train():
	for name in ("train_images", "train_labels", "val_images", "val_labels"):
		if not os.path.exists(name):
			raise SystemExit("ERROR: '%s' not found. Run load_images.py first." % name)
	with open("train_images", "rb") as f:
		train_images = np.array(pickle.load(f))
	with open("train_labels", "rb") as f:
		train_labels = np.array(pickle.load(f), dtype=np.int32)

	with open("val_images", "rb") as f:
		val_images = np.array(pickle.load(f))
	with open("val_labels", "rb") as f:
		val_labels = np.array(pickle.load(f), dtype=np.int32)

	train_images = np.reshape(train_images, (train_images.shape[0], image_x, image_y, 1))
	val_images = np.reshape(val_images, (val_images.shape[0], image_x, image_y, 1))
	num_of_classes = get_num_of_classes()
	train_labels = to_categorical(train_labels, num_classes=num_of_classes)
	val_labels = to_categorical(val_labels, num_classes=num_of_classes)

	print(val_labels.shape)

	model, callbacks_list = cnn_model()
	model.summary()
	model.fit(train_images, train_labels, validation_data=(val_images, val_labels), epochs=15, batch_size=500, callbacks=callbacks_list)
	scores = model.evaluate(val_images, val_labels, verbose=0)
	print("CNN Error: %.2f%%" % (100-scores[1]*100))
	#model.save('cnn_model_keras2.keras')

if __name__ == "__main__":
	train()
