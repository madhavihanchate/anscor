from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(16), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(32))
    password = db.Column(db.String(256), nullable=False)
    sex = db.Column(db.String(20))
    dob = db.Column(db.Date)
    blood_group = db.Column(db.String(8))
    country = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Record(db.Model):
    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    prediction = db.Column(db.String(64))
    confidence = db.Column(db.String(32))
    hemoglobin = db.Column(db.String(32))
    image_path = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
