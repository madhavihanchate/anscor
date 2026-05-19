"""
ANISOR  —  SQLite Database Module
Handles patient accounts and diagnosis record storage.
"""

import os
import sqlite3
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ── Database path ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "anscor.db")


# ── Helpers ───────────────────────────────────────────────────
def get_db():
    """Return a new database connection (auto-creates file if missing)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # dict-like rows
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they don't exist yet."""
    conn = get_db()
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  TEXT    UNIQUE NOT NULL,
            name        TEXT    NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            phone       TEXT,
            password    TEXT    NOT NULL,
            sex         TEXT,
            dob         TEXT,
            blood_group TEXT,
            country     TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  TEXT    NOT NULL,
            result      TEXT    NOT NULL,
            confidence  TEXT,
            hemoglobin  TEXT,
            symptoms    TEXT,
            image_path  TEXT,
            exam_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    conn.commit()
    conn.close()
    print("[OK] Database initialised:", DB_PATH)


# ── Patient CRUD ──────────────────────────────────────────────
def create_patient(data):
    """
    Register a new patient.
    `data` must contain: name, email, password
    Optional: phone, sex, dob, blood_group, country, patient_id
    Returns the patient dict or raises ValueError on duplicate email.
    """
    import math, random
    patient_id = data.get("patient_id") or ("P" + str(math.floor(100000 + random.random() * 900000)))

    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO patients
               (patient_id, name, email, phone, password, sex, dob, blood_group, country)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                patient_id,
                data["name"],
                data["email"],
                data.get("phone", ""),
                generate_password_hash(data["password"]),
                data.get("sex", ""),
                data.get("dob", ""),
                data.get("blood_group", ""),
                data.get("country", ""),
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        if "email" in str(e):
            raise ValueError("Email already registered.")
        raise ValueError("Patient ID conflict — please try again.")
    finally:
        conn.close()

    return get_patient_by_id(patient_id)


def authenticate(email, password):
    """
    Check credentials. Returns patient dict on success, None on failure.
    """
    conn = get_db()
    row  = conn.execute(
        "SELECT * FROM patients WHERE email = ?", (email,)
    ).fetchone()
    conn.close()

    if row is None:
        return None
    if not check_password_hash(row["password"], password):
        return None

    return _row_to_patient(row)


def get_patient_by_id(patient_id):
    """Fetch a single patient by their patient_id string."""
    conn = get_db()
    row  = conn.execute(
        "SELECT * FROM patients WHERE patient_id = ?", (patient_id,)
    ).fetchone()
    conn.close()
    return _row_to_patient(row) if row else None


def get_patient_by_email(email):
    """Fetch a single patient by email."""
    conn = get_db()
    row  = conn.execute(
        "SELECT * FROM patients WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return _row_to_patient(row) if row else None


def _row_to_patient(row):
    """Convert a sqlite3.Row to a plain dict (excluding password)."""
    return {
        "patient_id":  row["patient_id"],
        "name":        row["name"],
        "email":       row["email"],
        "phone":       row["phone"],
        "sex":         row["sex"],
        "dob":         row["dob"],
        "blood_group": row["blood_group"],
        "country":     row["country"],
        "created_at":  row["created_at"],
    }


# ── Record CRUD ───────────────────────────────────────────────
def save_record(data):
    """
    Save a diagnosis record.
    `data` must contain: patient_id, result
    Optional: confidence, hemoglobin, symptoms (list), image_path
    """
    symptoms_json = json.dumps(data.get("symptoms", []))

    conn = get_db()
    conn.execute(
        """INSERT INTO records
           (patient_id, result, confidence, hemoglobin, symptoms, image_path)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            data["patient_id"],
            data["result"],
            data.get("confidence", "0%"),
            data.get("hemoglobin", "0 g/dL"),
            symptoms_json,
            data.get("image_path", ""),
        ),
    )
    conn.commit()
    conn.close()


def get_records(patient_id):
    """Return all diagnosis records for a patient, newest first."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM records WHERE patient_id = ? ORDER BY exam_date DESC",
        (patient_id,),
    ).fetchall()
    conn.close()

    return [
        {
            "id":         r["id"],
            "patient_id": r["patient_id"],
            "result":     r["result"],
            "confidence": r["confidence"],
            "hemoglobin": r["hemoglobin"],
            "symptoms":   json.loads(r["symptoms"]) if r["symptoms"] else [],
            "image_path": r["image_path"],
            "exam_date":  r["exam_date"],
        }
        for r in rows
    ]
