# ANISOR

**AI-Based Non-Invasive Anemia Screening System**

ANISOR uses deep learning to detect potential anemia from fingernail images. Users upload a photo of their nails, complete a symptom survey, and receive an instant AI-powered screening result with hemoglobin estimation and confidence score.

---

## Features

- **AI Image Analysis** — ResNet50-based model classifies nail images to detect anemia indicators
- **Symptom Survey** — 11-symptom checklist (fatigue, pallor, dizziness, etc.) submitted alongside the image
- **Patient Database** — SQLite backend stores patient accounts and full diagnosis history
- **Secure Authentication** — Password hashing via Werkzeug; signup/login with server-side validation
- **Past Records** — Patients can view all their previous diagnoses on the profile page
- **Result Dashboard** — Detailed result page with prediction, confidence, hemoglobin estimate, symptoms, and recommendation

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML, CSS, JavaScript |
| **Backend** | Python 3.11, Flask, Flask-CORS |
| **AI Model** | TensorFlow / Keras, ResNet50 (transfer learning) |
| **Database** | SQLite |
| **Auth** | Werkzeug password hashing |

---

## Project Structure

```
anscor-ai/
├── index.html              # Login page
├── signup.html              # Registration page
├── home.html                # Home / landing page
├── upload.html              # Image upload + symptom survey
├── result.html              # Diagnosis result dashboard
├── profile.html             # Patient profile + past records
├── script.js                # Frontend logic (auth, upload, navigation)
├── style.css                # All styles
├── assets/                  # Background images
│   ├── bg.jpg
│   └── medical.jpg
├── backend/
│   ├── app.py               # Flask server — API endpoints
│   ├── predict.py            # TensorFlow prediction logic
│   ├── database.py           # SQLite CRUD (patients + records)
│   ├── train_model.py        # Model training script (ResNet50)
│   ├── requirements.txt      # Python dependencies
│   ├── models/
│   │   └── resnet50_model.h5 # Trained model weights
│   ├── classified/           # Training dataset (healthy / unhealthy)
│   ├── uploads/              # Uploaded images (runtime)
│   ├── anscor.db             # SQLite database (auto-created)
│   └── venv/                 # Python 3.11 virtual environment
└── README.md
```

---

## Setup & Installation

### Prerequisites

- **Python 3.11** (TensorFlow does not support Python 3.13+)
- pip

### 1. Clone the repository

```bash
git clone https://github.com/premsule404/anscor-ai.git
cd anscor-ai
```

### 2. Create a Python 3.11 virtual environment

```bash
cd backend
python3.11 -m venv venv
```

### 3. Install dependencies

```bash
# Windows
.\venv\Scripts\pip.exe install -r requirements.txt

# macOS/Linux
./venv/bin/pip install -r requirements.txt
```

### 4. Run the server

```bash
# Windows (from project root)
.\backend\venv\Scripts\python.exe .\backend\app.py

# macOS/Linux
./backend/venv/bin/python ./backend/app.py
```

The server starts at **http://127.0.0.1:5000**

---

## Usage

1. **Register** — Go to `/signup.html`, create an account
2. **Login** — Sign in with your credentials at `/` or `/index.html`
3. **Upload** — Click "Check Anemia" on the home page, upload a nail image, complete the symptom survey
4. **Analyze** — Click "Analyze Image" to get your AI screening result
5. **Profile** — View your patient info and all past diagnosis records

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/signup` | POST | Register a new patient |
| `/api/login` | POST | Authenticate and return patient data |
| `/api/patient/<id>` | GET | Fetch patient profile |
| `/api/records/<id>` | GET | Fetch all past diagnosis records |
| `/api/records` | POST | Save a diagnosis record |
| `/upload` | POST | Upload image for AI prediction (auto-saves record) |
| `/predict` | GET | Health check — verify prediction engine is loaded |

---

## Training the Model

Place training images in `backend/classified/` with two subdirectories:

```
classified/
├── healthy/      # Nail images from non-anemic patients
└── unhealthy/    # Nail images from anemic patients
```

Then run:

```bash
.\backend\venv\Scripts\python.exe .\backend\train_model.py
```

The trained model is saved to `backend/models/resnet50_model.h5`.

---

## Database Schema

**patients** — One row per registered user

| Column | Type | Description |
|--------|------|-------------|
| patient_id | TEXT | Unique ID (e.g. P123456) |
| name | TEXT | Full name |
| email | TEXT | Email (unique) |
| phone | TEXT | Phone number |
| password | TEXT | Hashed password |
| sex | TEXT | Male / Female / Other |
| dob | TEXT | Date of birth |
| blood_group | TEXT | Blood group |
| country | TEXT | Country |

**records** — One row per diagnosis

| Column | Type | Description |
|--------|------|-------------|
| patient_id | TEXT | FK to patients |
| result | TEXT | Prediction result |
| confidence | TEXT | Model confidence % |
| hemoglobin | TEXT | Estimated hemoglobin range |
| symptoms | TEXT | JSON array of selected symptoms |
| image_path | TEXT | Filename of uploaded image |
| exam_date | DATETIME | Timestamp of diagnosis |

---

## Disclaimer

> This is an AI-based screening tool and **not a medical diagnosis**. Please consult a healthcare professional for confirmation and treatment.

---

## License

This project is for educational and research purposes.
