import os
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.applications import ResNet50
from keras.models import Sequential
from keras.layers import Dense, GlobalAveragePooling2D, Dropout
from keras.optimizers import Adam

# DATASET PATH
dataset_path = "classified"

# IMAGE SETTINGS
IMG_SIZE = 224
BATCH_SIZE = 16

if not os.path.isdir(dataset_path):
    raise FileNotFoundError(f"Dataset folder not found: {dataset_path}")

os.makedirs("models", exist_ok=True)

# LOAD DATA
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

train_data = train_datagen.flow_from_directory(
    dataset_path,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='training'
)

val_data = train_datagen.flow_from_directory(
    dataset_path,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='validation'
)

print(train_data.class_indices)

# LOAD RESNET50
base_model = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(224,224,3)
)

base_model.trainable = False

# MODEL
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=Adam(),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# TRAIN
model.fit(
    train_data,
    validation_data=val_data,
    epochs=5
)

# SAVE MODEL
model.save("models/resnet50_model.h5")

print("MODEL TRAINED SUCCESSFULLY")
