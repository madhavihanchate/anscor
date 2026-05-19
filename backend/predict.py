import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import os

# Base directory for absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# LOAD MODEL
MODEL_PATH = os.path.join(BASE_DIR, "models/resnet50_model.h5")

# Load model globally to avoid reloading on every request
if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH)
else:
    model = None
    print(f"CRITICAL: Model not found at {MODEL_PATH}")

def predict_anemia(img_path):
    try:
        if model is None:
            return {
                "result": "Model Not Loaded",
                "confidence": "0%",
                "hemoglobin": "0 g/dL"
            }

        # CHECK FILE
        if not os.path.exists(img_path):
            return {
                "result": "Image Not Found",
                "confidence": "0%",
                "hemoglobin": "0 g/dL"
            }

        # LOAD IMAGE
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0

        # PREDICTION
        prediction = model.predict(img_array)[0][0]
        print("RAW PREDICTION:", prediction)

        # RESULT
        if prediction > 0.5:
            result = "Potential Anemia Detected"
            hb = "8-10 g/dL"
            confidence = round(float(prediction) * 100, 2)
        else:
            result = "No Anemia Detected"
            hb = "12-15 g/dL"
            confidence = round((1 - float(prediction)) * 100, 2)

        return {
            "result": result,
            "confidence": f"{confidence}%",
            "hemoglobin": hb
        }

    except Exception as e:
        import traceback
        print("PREDICTION ERROR:", e)
        traceback.print_exc()
        return {
            "result": "Prediction Failed",
            "confidence": "0%",
            "hemoglobin": "0 g/dL"
        }
