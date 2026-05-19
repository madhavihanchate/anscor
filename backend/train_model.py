import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam
import os

# Set working directory to the script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

dataset_path = "classified"
model_dir = "models"
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

# Check for data
if not os.path.exists(dataset_path) or len(os.listdir(dataset_path)) < 2:
    print(f"ERROR: Dataset not found in {dataset_path}. Ensure 'healthy' and 'unhealthy' folders exist.")
    exit()

# Data Loaders
datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2, horizontal_flip=True, rotation_range=15)

train_gen = datagen.flow_from_directory(
    dataset_path, target_size=(224, 224), batch_size=16, class_mode='binary', subset='training'
)

val_gen = datagen.flow_from_directory(
    dataset_path, target_size=(224, 224), batch_size=16, class_mode='binary', subset='validation'
)

print(f"Classes: {train_gen.class_indices}")

# Build Model
base = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base.trainable = False

model = Sequential([
    base,
    GlobalAveragePooling2D(),
    Dense(128, activation='relu'),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer=Adam(learning_rate=0.0001), loss='binary_crossentropy', metrics=['accuracy'])

print("Starting Training...")
model.fit(train_gen, validation_data=val_gen, epochs=5)

# Save
save_path = os.path.join(model_dir, "resnet50_model.h5")
model.save(save_path)
print(f"SUCCESS: Model saved at {save_path}")
