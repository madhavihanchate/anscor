import os
import numpy as np

try:
    import onnxruntime as ort
    from PIL import Image
    ONNX_AVAILABLE = True
except Exception:
    ONNX_AVAILABLE = False

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "resnet50_model.onnx"
)

IMAGE_SIZE = (224, 224)

_session = None


def _load_model():
    global _session

    if _session is not None:
        return _session

    if not ONNX_AVAILABLE:
        return None

    if not os.path.exists(MODEL_PATH):
        return None

    _session = ort.InferenceSession(MODEL_PATH)
    return _session


def _preprocess_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize(IMAGE_SIZE)
    image_arr = np.array(image, dtype=np.float32) / 255.0
    image_arr = np.expand_dims(image_arr, axis=0)
    return image_arr


def predict_anemia(image_path):
    """Predict anemia from an image path and return a prediction dict."""
    session = _load_model()

    if session is None:
        return {
            "result": "Model not available",
            "confidence": "0%",
            "hemoglobin": "N/A"
        }

    try:
        image_arr = _preprocess_image(image_path)
        input_name = session.get_inputs()[0].name
        prediction = session.run(None, {input_name: image_arr})
        score = float(prediction[0][0][0])
        confidence = int(min(max(abs(score - 0.5) * 200, 50), 99))

        if score > 0.5:
            result = "Mild/Moderate Anemia Detected"
        else:
            result = "No Anemia Detected"

        hemoglobin = f"{round(13.0 - (score - 0.5) * 4.0, 1)} g/dL"

        return {
            "result": result,
            "confidence": f"{confidence}%",
            "hemoglobin": hemoglobin
        }
    except Exception as e:
        print("PREDICTION ERROR:", e)
        return {
            "result": "Prediction Failed",
            "confidence": "0%",
            "hemoglobin": "N/A"
        }
