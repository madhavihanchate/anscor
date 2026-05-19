import os
from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from predict import predict_anemia
from werkzeug.utils import secure_filename
from database import init_db, create_patient, authenticate, get_patient_by_id, save_record, get_records

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR  = os.path.abspath(os.path.join(BASE_DIR, ".."))   # project root

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

# ── Config ────────────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXT   = {"png", "jpg", "jpeg", "bmp", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT
    )


# ══════════════════════════════════════════════════════════════
#  FRONTEND ROUTES
# ══════════════════════════════════════════════════════════════

# ── Root — serve the login page ───────────────────────────────
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# ══════════════════════════════════════════════════════════════
#  AUTH & PATIENT API
# ══════════════════════════════════════════════════════════════

# ── Signup ────────────────────────────────────────────────────
@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json()

    # Validate required fields
    if not data:
        return jsonify({"status": "error", "message": "No data provided."}), 400

    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not name or not email or not password:
        return jsonify({"status": "error", "message": "Name, email, and password are required."}), 400

    try:
        patient = create_patient(data)
        return jsonify({"status": "success", "patient": patient})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 409


# ── Login ─────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data provided."}), 400

    email    = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required."}), 400

    patient = authenticate(email, password)

    if patient is None:
        return jsonify({"status": "error", "message": "Invalid email or password."}), 401

    return jsonify({"status": "success", "patient": patient})


# ── Get patient profile ───────────────────────────────────────
@app.route("/api/patient/<patient_id>", methods=["GET"])
def api_get_patient(patient_id):
    patient = get_patient_by_id(patient_id)

    if patient is None:
        return jsonify({"status": "error", "message": "Patient not found."}), 404

    return jsonify({"status": "success", "patient": patient})


# ══════════════════════════════════════════════════════════════
#  DIAGNOSIS RECORDS API
# ══════════════════════════════════════════════════════════════

# ── Save a record ─────────────────────────────────────────────
@app.route("/api/records", methods=["POST"])
def api_save_record():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data provided."}), 400

    patient_id = (data.get("patient_id") or "").strip()
    result     = (data.get("result") or "").strip()

    if not patient_id or not result:
        return jsonify({"status": "error", "message": "patient_id and result are required."}), 400

    save_record(data)
    return jsonify({"status": "success", "message": "Record saved."})


# ── Get all records for a patient ─────────────────────────────
@app.route("/api/records/<patient_id>", methods=["GET"])
def api_get_records(patient_id):
    records = get_records(patient_id)
    return jsonify({"status": "success", "records": records})


# ══════════════════════════════════════════════════════════════
#  PREDICTION ENDPOINTS (unchanged)
# ══════════════════════════════════════════════════════════════

# ── Health-check ──────────────────────────────────────────────
@app.route("/predict", methods=["GET", "POST"])
def health_check():
    from predict import model
    if model is None:
        return jsonify({
            "status": "error",
            "message": "Prediction engine not loaded on the server."
        }), 500
    return jsonify({
        "status": "ok",
        "message": "Prediction engine is active and ready!"
    })


# ── Main prediction endpoint ──────────────────────────────────
@app.route("/upload", methods=["POST"])
def upload():
    # 1. Check a file was sent
    if "image" not in request.files:
        return jsonify({"status": "error", "message": "No image file provided."}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"status": "error", "message": "Empty filename."}), 400

    if not allowed_file(file.filename):
        return jsonify({"status": "error", "message": "File type not allowed."}), 400

    # 2. Save file
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    # 3. Run prediction
    result = predict_anemia(save_path)

    # 4. Auto-save record if patient_id was included
    patient_id = request.form.get("patient_id", "").strip()
    symptoms   = request.form.get("symptoms", "[]")

    if patient_id:
        import json
        try:
            symptoms_list = json.loads(symptoms)
        except Exception:
            symptoms_list = []

        save_record({
            "patient_id": patient_id,
            "result":     result.get("result", "Unknown"),
            "confidence": result.get("confidence", "0%"),
            "hemoglobin": result.get("hemoglobin", "0 g/dL"),
            "symptoms":   symptoms_list,
            "image_path": filename,
        })

    # 5. Return result
    return jsonify({
        "status":     "success",
        "result":     result.get("result",     "Unknown"),
        "confidence": result.get("confidence", "0%"),
        "hemoglobin": result.get("hemoglobin", "0 g/dL")
    })


# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    print(f"[OK] Starting ANISOR backend on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
else:
    # When imported by gunicorn
    init_db()