import os
import tensorflow as tf

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(SCRIPT_DIR, "classified")
MODEL_PATH = os.path.join(SCRIPT_DIR, "models", "resnet50_model.h5")

IMG_SIZE = 224
BATCH_SIZE = 32

if not os.path.isdir(DATASET_PATH):
    raise FileNotFoundError(f"Dataset folder not found: {DATASET_PATH}")

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_PATH,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    validation_split=0.2,
    subset="training",
    seed=42,
    label_mode="binary",
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_PATH,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    validation_split=0.2,
    subset="validation",
    seed=42,
    label_mode="binary",
)

class_names = train_ds.class_names
print(f"Classes: {class_names}")

AUTOTUNE = tf.data.AUTOTUNE

data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomBrightness(0.2),
])

normalization = tf.keras.Sequential([
    tf.keras.layers.Rescaling(1.0 / 255),
])

train_ds = train_ds.map(
    lambda x, y: (normalization(data_augmentation(x, training=True), training=False), y),
    num_parallel_calls=AUTOTUNE,
).prefetch(AUTOTUNE)

val_ds = val_ds.map(
    lambda x, y: (normalization(x), y),
    num_parallel_calls=AUTOTUNE,
).prefetch(AUTOTUNE)

# Compute class weights
total = sum(1 for _ in os.listdir(os.path.join(DATASET_PATH, class_names[0]))) + \
        sum(1 for _ in os.listdir(os.path.join(DATASET_PATH, class_names[1])))
n_class0 = sum(1 for _ in os.listdir(os.path.join(DATASET_PATH, class_names[0])))
n_class1 = total - n_class0
weight0 = total / (2.0 * max(n_class0, 1))
weight1 = total / (2.0 * max(n_class1, 1))
class_weights = {0: weight0, 1: weight1}
print(f"Class weights: {class_weights} (total: {total}, {class_names[0]}: {n_class0}, {class_names[1]}: {n_class1})")

# BUILD MODEL
base_model = tf.keras.applications.ResNet50(
    weights="imagenet",
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
)

base_model.trainable = False

model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(256, activation="relu"),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(1, activation="sigmoid"),
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss="binary_crossentropy",
    metrics=["accuracy"],
)

callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-6),
]

print("\n=== Phase 1: Frozen backbone, 10 epochs ===")
model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10,
    class_weight=class_weights,
    callbacks=callbacks,
)

# Phase 2: unfreeze last 30 layers
print("\n=== Phase 2: Fine-tuning last 30 layers, 10 epochs ===")
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss="binary_crossentropy",
    metrics=["accuracy"],
)

model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10,
    class_weight=class_weights,
    callbacks=callbacks,
)

val_loss, val_acc = model.evaluate(val_ds)
print(f"\nFinal validation accuracy: {val_acc:.4f}")

model.save(MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")
