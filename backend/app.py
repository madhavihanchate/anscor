from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from flask_cors import CORS

import os

from predict import predict_anemia
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random

# database
from db import db, Patient, Record


# ======================
# FLASK APP
# ======================

app = Flask(__name__)

CORS(app)

# ----------------------
# Database configuration
# ----------------------
db_path = os.path.join(
    os.path.dirname(__file__),
    "anscor.db"
)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ======================
# FRONTEND ROUTES
# ======================

@app.route("/")
def home():

    return send_from_directory(
        "../",
        "index.html"
    )


@app.route("/<path:path>")
def static_files(path):

    return send_from_directory(
        "../",
        path
    )


# ======================
# UPLOAD FOLDER
# ======================

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):

    os.makedirs(UPLOAD_FOLDER)


# ======================
# PREDICTION ROUTE
# ======================

@app.route(
    "/predict",
    methods=["POST"]
)

def predict():

    try:

        # CHECK IMAGE

        if "image" not in request.files:

            return jsonify({
                "result":
                "No image uploaded"
            }), 400

        file = request.files["image"]
           

        # CHECK EMPTY FILE

        if file.filename == "":

            return jsonify({
                "result":
                "No selected file"
            }), 400

        # SAVE IMAGE

        filepath =os.path.join(
            
                UPLOAD_FOLDER,
                file.filename
            )

        file.save(filepath)

        # PREDICT

        prediction_data = predict_anemia(filepath)
           

        print(prediction_data)

        # store record if patient id provided
        try:

            patient_pid = request.form.get("patientId")

            if patient_pid:

                patient = Patient.query.filter_by(

                    patient_id=patient_pid

                ).first()

                if patient:

                    rec = Record(

                        patient_id=patient.id,

                        prediction=prediction_data.get("result"),

                        confidence=prediction_data.get("confidence"),

                        hemoglobin=prediction_data.get("hemoglobin"),

                        image_path=filepath

                    )

                    db.session.add(rec)

                    db.session.commit()

        except Exception as e:

            print("RECORD SAVE FAILED:", e)

        # RETURN RESULT

        return jsonify({
            "prediction": {
                "result": prediction_data["result"],
                "confidence": prediction_data["confidence"],
                "hemoglobin": prediction_data["hemoglobin"]
            }
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({

            "result":
                "Prediction Failed",

            "confidence":
                "0%",

            "hemoglobin":
                "0 g/dL"

        }), 500


# ======================
# SIGNUP ROUTE
# ======================


@app.route(
    "/signup",
    methods=["POST"]
)
def signup():

    try:

        data = request.get_json() or {}

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")
        sex = data.get("sex")
        dob = data.get("dob")
        blood = data.get("blood")
        country = data.get("country")

        # validate
        if not (name and email and password):

            return jsonify({
                "status": "error",
                "message": "Missing required fields"
            }), 400

        # check existing email
        existing = Patient.query.filter_by(email=email).first()

        if existing:

            return jsonify({
                "status": "error",
                "message": "Email already registered"
            }), 400

        # generate unique patient id
        patient_id = None

        while True:

            pid = "P" + str(random.randint(100000, 999999))

            if not Patient.query.filter_by(patient_id=pid).first():

                patient_id = pid

                break

        # hash password
        hashed = generate_password_hash(password)

        # parse dob if provided
        dob_date = None

        if dob:

            try:

                dob_date = datetime.strptime(dob, "%Y-%m-%d").date()

            except Exception:

                dob_date = None

        # create patient
        patient = Patient(

            patient_id=patient_id,
            name=name,
            email=email,
            phone=phone,
            password=hashed,
            sex=sex,
            dob=dob_date,
            blood_group=blood,
            country=country

        )

        db.session.add(patient)

        db.session.commit()

        return jsonify({
            "status": "success",
            "patientId": patient_id
        }), 201

    except Exception as e:

        print("SIGNUP ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Signup failed"
        }), 500


# ======================
# LOGIN ROUTE
# ======================


@app.route(
    "/login",
    methods=["POST"]
)
def login():
    try:
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        if not (email and password):
            return jsonify({
                "status": "error",
                "message": "Email and password are required"
            }), 400

        patient = Patient.query.filter_by(email=email).first()

        if not patient or not check_password_hash(patient.password, password):
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        return jsonify({
            "status": "success",
            "patient": {
                "patientId": patient.patient_id,
                "name": patient.name,
                "email": patient.email,
                "phone": patient.phone,
                "sex": patient.sex,
                "dob": patient.dob.isoformat() if patient.dob else None,
                "blood": patient.blood_group,
                "country": patient.country
            }
        }), 200

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({
            "status": "error",
            "message": "Login failed"
        }), 500


# ======================
# RUN APP
# ======================

if __name__ == "__main__":

    app.run(
        debug=True
    )