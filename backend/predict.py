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


def _color_analysis(image_path):
    """Analyze nail bed color to estimate hemoglobin and anemia status.

    Healthy nail beds are pink/red due to blood flow.
    Anemic nail beds appear pale/white due to low hemoglobin.
    """
    image = Image.open(image_path).convert("RGB")
    image = image.resize(IMAGE_SIZE)
    arr = np.array(image, dtype=np.float32) / 255.0

    h, w = arr.shape[:2]
    cy, cx = h // 2, w // 2
    size = min(h, w) // 4
    center = arr[
        cy - size:cy + size,
        cx - size:cx + size
    ]

    r_mean = float(np.mean(center[:, :, 0]))
    g_mean = float(np.mean(center[:, :, 1]))
    b_mean = float(np.mean(center[:, :, 2]))
    brightness = (r_mean + g_mean + b_mean) / 3.0

    red_ratio = r_mean / max(brightness, 0.01)
    pinkness = max(0, min(1, (red_ratio - 0.9) / 0.4))

    hemoglobin = 8.0 + pinkness * 7.0
    hemoglobin = round(max(6.0, min(17.0, hemoglobin)), 1)

    if hemoglobin >= 12.0:
        result = "No Anemia Detected"
        confidence = int(min(50 + (hemoglobin - 12.0) * 10, 95))
    elif hemoglobin >= 10.0:
        result = "Mild Anemia Detected"
        confidence = int(min(50 + (12.0 - hemoglobin) * 12, 95))
    else:
        result = "Moderate/Severe Anemia Detected"
        confidence = int(min(50 + (10.0 - hemoglobin) * 8, 95))

    return {
        "result": result,
        "confidence": f"{confidence}%",
        "hemoglobin": f"{hemoglobin} g/dL",
        "debug": {
            "red_ratio": round(red_ratio, 4),
            "pinkness": round(pinkness, 4),
            "brightness": round(brightness, 4),
        }
    }


def predict_anemia(image_path):
    """Predict anemia from an image path and return a prediction dict."""
    try:
        result = _color_analysis(image_path)
        print(f"PREDICTION: {result['result']} | "
              f"Confidence: {result['confidence']} | "
              f"Hb: {result['hemoglobin']} | "
              f"Debug: {result.get('debug', {})}")
        return {
            "result": result["result"],
            "confidence": result["confidence"],
            "hemoglobin": result["hemoglobin"]
        }
    except Exception as e:
        print("PREDICTION ERROR:", e)
        return {
            "result": "Prediction Failed",
            "confidence": "0%",
            "hemoglobin": "N/A"
        }
