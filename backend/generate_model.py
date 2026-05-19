import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

# 1. Create a simple Neural Network (The Brain)
model = models.Sequential([
    layers.Input(shape=(224, 224, 3)), # Assuming 224x224 RGB images
    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(1, activation='sigmoid') # Output: 0 (No Anemia) to 1 (Anemia)
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 2. Save the "Brain" to a file
model.save('anemia_model.h5')

print("✅ Success: 'anemia_model.h5' has been generated!")
print("Now you can run your app.py.")