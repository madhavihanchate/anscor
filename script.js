// ============================================================
//  ANISOR  —  Frontend Logic
//  All pages share this script.
// ============================================================

const API_BASE = "";


// ────────────────────────────────────────────────────────────
//  SIGNUP  (signup.html)
// ────────────────────────────────────────────────────────────
function signup() {
    const name     = (document.getElementById("name")     || {}).value || "";
    const email    = (document.getElementById("email")    || {}).value || "";
    const phone    = (document.getElementById("phone")    || {}).value || "";
    const password = (document.getElementById("password") || {}).value || "";
    const sex      = (document.getElementById("sex")      || {}).value || "";
    const dob      = (document.getElementById("dob")      || {}).value || "";
    const blood    = (document.getElementById("blood")    || {}).value || "";
    const country  = (document.getElementById("country")  || {}).value || "";

    if (!name.trim() || !email.trim() || !password.trim()) {
        alert("Please fill in Name, Email, and Password.");
        return;
    }

    fetch(`${API_BASE}/api/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name:        name.trim(),
            email:       email.trim(),
            phone:       phone.trim(),
            password:    password.trim(),
            sex:         sex,
            dob:         dob,
            blood_group: blood,
            country:     country.trim()
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status !== "success") {
            alert("Signup failed: " + data.message);
            return;
        }

        // Store patient info locally for quick access
        const p = data.patient;
        localStorage.setItem("patientId",   p.patient_id);
        localStorage.setItem("name",        p.name);
        localStorage.setItem("email",       p.email);
        localStorage.setItem("phone",       p.phone);
        localStorage.setItem("sex",         p.sex);
        localStorage.setItem("dob",         p.dob);
        localStorage.setItem("blood",       p.blood_group);
        localStorage.setItem("country",     p.country);

        alert("Account created successfully! Please sign in.");
        window.location.href = "index.html";
    })
    .catch(err => {
        console.error("Signup error:", err);
        alert("Could not connect to server. Make sure backend is running.");
    });
}


// ────────────────────────────────────────────────────────────
//  LOGIN  (index.html)
// ────────────────────────────────────────────────────────────
function login() {
    const email    = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
        alert("Please enter your email and password.");
        return;
    }

    fetch(`${API_BASE}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status !== "success") {
            alert("Login failed: " + data.message);
            return;
        }

        // Store patient info locally
        const p = data.patient;
        localStorage.setItem("patientId",   p.patient_id);
        localStorage.setItem("name",        p.name);
        localStorage.setItem("email",       p.email);
        localStorage.setItem("phone",       p.phone);
        localStorage.setItem("sex",         p.sex);
        localStorage.setItem("dob",         p.dob);
        localStorage.setItem("blood",       p.blood_group);
        localStorage.setItem("country",     p.country);

        window.location.href = "home.html";
    })
    .catch(err => {
        console.error("Login error:", err);
        alert("Could not connect to server. Make sure backend is running.");
    });
}


// ────────────────────────────────────────────────────────────
//  NAVIGATION HELPERS
// ────────────────────────────────────────────────────────────
function goProfile() {
    window.location.href = "profile.html";
}

function goUpload() {
    window.location.href = "upload.html";
}

function goHome() {
    window.location.href = "home.html";
}


// ────────────────────────────────────────────────────────────
//  SYMPTOM SUBMIT  (upload.html — "Submit Symptoms" button)
// ────────────────────────────────────────────────────────────
function submitSymptoms() {
    const checkboxes = document.querySelectorAll(
        ".symptom-row input[type='checkbox']:checked"
    );

    const symptoms = Array.from(checkboxes).map(cb => cb.value);

    localStorage.setItem("symptoms", JSON.stringify(symptoms));

    alert(
        symptoms.length > 0
            ? `${symptoms.length} symptom(s) saved.`
            : "No symptoms selected — saved as none."
    );
}


// ────────────────────────────────────────────────────────────
//  VALIDATE SURVEY  (upload.html — "Analyze Image" button)
// ────────────────────────────────────────────────────────────
function validateSurvey() {
    const fileInput = document.getElementById("fileInput");

    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert("Please select a nail image before analyzing.");
        return;
    }

    // Auto-save symptoms before analyzing
    submitSymptoms();

    // Proceed to analysis
    analyzeImage(fileInput.files[0]);
}


// ────────────────────────────────────────────────────────────
//  ANALYZE IMAGE  — sends image to backend, stores result
// ────────────────────────────────────────────────────────────
function analyzeImage(file) {
    const analyzeBtn = document.getElementById("analyzeBtn");

    if (analyzeBtn) {
        analyzeBtn.innerText   = "Analyzing…";
        analyzeBtn.disabled    = true;
    }

    // Save a base64 preview of the image for result.html
    const reader = new FileReader();
    reader.onload = function (e) {
        localStorage.setItem("uploadedImage", e.target.result);
    };
    reader.readAsDataURL(file);

    // Build multipart form data
    const formData = new FormData();
    formData.append("image", file);

    // Include patient_id and symptoms so backend auto-saves the record
    const patientId = localStorage.getItem("patientId") || "";
    const symptoms  = localStorage.getItem("symptoms")  || "[]";
    formData.append("patient_id", patientId);
    formData.append("symptoms",   symptoms);

    fetch(`${API_BASE}/upload`, {
        method: "POST",
        body:   formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.message || "Server error"); });
        }
        return response.json();
    })
    .then(data => {
        if (data.status !== "success") {
            throw new Error(data.message || "Prediction failed.");
        }

        // Store results for result.html
        localStorage.setItem("prediction",  data.result);
        localStorage.setItem("confidence",  data.confidence);
        localStorage.setItem("hemoglobin",  data.hemoglobin);

        // Redirect to results page
        window.location.href = "result.html";
    })
    .catch(error => {
        console.error("Analysis error:", error);
        alert("Error: " + error.message + "\n\nMake sure backend/app.py is running.");

        if (analyzeBtn) {
            analyzeBtn.innerText  = "Analyze Image";
            analyzeBtn.disabled   = false;
        }
    });
}


// ────────────────────────────────────────────────────────────
//  LOAD PROFILE  (profile.html)
// ────────────────────────────────────────────────────────────
function loadProfile() {
    const patientId = localStorage.getItem("patientId");

    // Populate from localStorage first (instant)
    setText("name",    localStorage.getItem("name"));
    setText("email",   localStorage.getItem("email"));
    setText("phone",   localStorage.getItem("phone"));
    setText("sex",     localStorage.getItem("sex"));
    setText("dob",     localStorage.getItem("dob"));
    setText("blood",   localStorage.getItem("blood"));
    setText("country", localStorage.getItem("country"));
    setText("pid",     patientId);

    // Calculate age from DOB
    const dob = localStorage.getItem("dob");
    if (dob) {
        const age = Math.floor((Date.now() - new Date(dob).getTime()) / (365.25 * 24 * 60 * 60 * 1000));
        setText("age", age + " years");
    }

    // Then fetch fresh data from backend
    if (patientId) {
        fetch(`${API_BASE}/api/patient/${patientId}`)
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                const p = data.patient;
                setText("name",    p.name);
                setText("email",   p.email);
                setText("phone",   p.phone);
                setText("sex",     p.sex);
                setText("dob",     p.dob);
                setText("blood",   p.blood_group);
                setText("country", p.country);
            }
        })
        .catch(err => console.warn("Could not fetch profile from server:", err));

        // Load past records
        loadRecords(patientId);
    }
}


// ────────────────────────────────────────────────────────────
//  LOAD RECORDS  (profile.html — past diagnosis history)
// ────────────────────────────────────────────────────────────
function loadRecords(patientId) {
    const container = document.getElementById("recordsContainer");
    if (!container) return;

    fetch(`${API_BASE}/api/records/${patientId}`)
    .then(res => res.json())
    .then(data => {
        if (data.status !== "success" || !data.records || data.records.length === 0) {
            container.innerHTML = "<p class='no-records'>No past diagnosis records found.</p>";
            return;
        }

        let html = "";
        data.records.forEach((r, i) => {
            const date      = new Date(r.exam_date).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
            const isAnemia  = r.result.toLowerCase().includes("anemia") && r.result.toLowerCase().includes("detected");
            const badgeClass = isAnemia ? "badge-warning" : "badge-ok";
            const symptoms   = r.symptoms && r.symptoms.length > 0 ? r.symptoms.join(", ") : "None";

            html += `
                <div class="record-card">
                    <div class="record-header">
                        <span class="record-date">${date}</span>
                        <span class="record-badge ${badgeClass}">${r.result}</span>
                    </div>
                    <div class="record-details">
                        <p><b>Confidence:</b> ${r.confidence}</p>
                        <p><b>Hemoglobin:</b> ${r.hemoglobin}</p>
                        <p><b>Symptoms:</b> ${symptoms}</p>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    })
    .catch(err => {
        console.warn("Could not load records:", err);
        container.innerHTML = "<p class='no-records'>Could not load records from server.</p>";
    });
}


// ────────────────────────────────────────────────────────────
//  UTILITY
// ────────────────────────────────────────────────────────────
function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.innerText = value || "—";
}