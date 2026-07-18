// ======================
// LOGIN FUNCTION
// ======================

async function login() {

    let email = document.getElementById("email")?.value;
    let password = document.getElementById("password")?.value;

    if (!email || !password) {

        alert("Please enter email and password");
        return;
    }

    try {

        const response = await fetch("/login", {

            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.status === "error") {

            alert(data.message);
            return;
        }

        // Store patient data from server
        let patient = data.patient;

        localStorage.setItem("patientId", patient.patientId);
        localStorage.setItem("name", patient.name);
        localStorage.setItem("email", patient.email);
        localStorage.setItem("phone", patient.phone || "");
        localStorage.setItem("sex", patient.sex || "");
        localStorage.setItem("dob", patient.dob || "");
        localStorage.setItem("blood", patient.blood || "");
        localStorage.setItem("country", patient.country || "");

        window.location.href = "home.html";

    } catch (error) {

        console.error(error);
        alert("Cannot connect to server. Please try again.");
    }
}


// ======================
// SIGNUP FUNCTION
// ======================

async function signup() {

    let name = document.getElementById("name")?.value;
    let email = document.getElementById("email")?.value;
    let phone = document.getElementById("phone")?.value;
    let password = document.getElementById("password")?.value;
    let sex = document.getElementById("sex")?.value;
    let dob = document.getElementById("dob")?.value;
    let blood = document.getElementById("blood")?.value;
    let country = document.getElementById("country")?.value;

    if (
        !name ||
        !email ||
        !phone ||
        !password ||
        !sex ||
        !dob ||
        !blood ||
        !country
    ) {

        alert("Please fill all fields");
        return;
    }

    try {

        const response = await fetch("/signup", {

            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name, email, phone, password,
                sex, dob, blood, country
            })
        });

        const data = await response.json();

        if (data.status === "error") {

            alert(data.message);
            return;
        }

        // Store patient data (no password!)
        localStorage.setItem("patientId", data.patientId);
        localStorage.setItem("name", name);
        localStorage.setItem("email", email);
        localStorage.setItem("phone", phone);
        localStorage.setItem("sex", sex);
        localStorage.setItem("dob", dob);
        localStorage.setItem("blood", blood);
        localStorage.setItem("country", country);

        alert("Signup Successful");

        window.location.href = "index.html";

    } catch (error) {

        console.error(error);
        alert("Cannot connect to server. Please try again.");
    }
}


// ======================
// NAVIGATION
// ======================

function goUpload() {

    window.location.href = "upload.html";
}

function goProfile() {

    window.location.href = "profile.html";
}


// ======================
// VALIDATE SURVEY
// ======================

function validateSurvey() {

    let fileInput =
        document.getElementById("fileInput");

    if (!fileInput || fileInput.files.length === 0) {

        alert("Please upload image first!");
        return;
    }

    alert("Image Selected Successfully");
}


// ======================
// SUBMIT SYMPTOMS
// ======================

async function submitSymptoms() {

    let fileInput =
        document.getElementById("fileInput");

    if (!fileInput || fileInput.files.length === 0) {

        alert("Please upload image first!");
        return;
    }

    // ======================
    // GET SYMPTOMS
    // ======================

    let symptoms = [];

    document
        .querySelectorAll(
            '.symptom-row input[type="checkbox"]:checked'
        )
        .forEach((cb) => {

            symptoms.push(cb.value);
        });

    if (symptoms.length === 0) {

        alert("Please select symptoms!");
        return;
    }

    // SAVE SYMPTOMS

    localStorage.setItem(
        "symptoms",
        JSON.stringify(symptoms)
    );

    // ======================
    // SAVE IMAGE
    // ======================

    let file =
        fileInput.files[0];

    let reader =
        new FileReader();

    reader.onload = async function (e) {

        localStorage.setItem(
            "uploadedImage",
            e.target.result
        );

        // ======================
        // CREATE FORM DATA
        // ======================

        let formData =
            new FormData();

        formData.append(
            "image",
            file
        );

        let patientId =
            localStorage.getItem(
                "patientId"
            );

        if (patientId) {

            formData.append(
                "patientId",
                patientId
            );
        }

        try {

            const response =
                await fetch(
                    "/predict",
                    {
                        method: "POST",
                        body: formData
                    }
                );

            if (!response.ok) {

                throw new Error(
                    "Server Error"
                );
            }

            const data =
                await response.json();

            console.log(data);

            // ======================
            // SAVE RESULT
            // ======================

            localStorage.setItem(
                "prediction",
                data.prediction.result
            );

            let conf = String(data.prediction.confidence);

            localStorage.setItem(
                "confidence",
                conf.endsWith("%") ? conf : conf + "%"
            );

            localStorage.setItem(
                "hemoglobin",
                data.prediction.hemoglobin
            );

            // ======================
            // PATIENT ID
            // ======================

            // patientId is already set by login/signup from server

            // ======================
            // GO RESULT PAGE
            // ======================

            window.location.href =
                "result.html";

        } catch (error) {

            console.error(error);

            alert(
                "Backend connection failed!"
            );
        }
    };

    reader.readAsDataURL(file);
}


// ======================
// ANALYZE SYMPTOMS
// ======================

function analyzeSymptoms() {

    const symptoms =
        JSON.parse(
            localStorage.getItem(
                "symptoms"
            )
        ) || [];

    let symptomList =
        document.getElementById(
            "symptomList"
        );

    if (!symptomList) return;

    symptomList.innerHTML = "";

    symptoms.forEach((symptom) => {

        let li =
            document.createElement("li");

        li.innerText = symptom;

        symptomList.appendChild(li);
    });
}


// ======================
// PAGE LOAD
// ======================

window.onload = function () {

    // ======================
    // RESULT PAGE
    // ======================

    let prediction =
        localStorage.getItem(
            "prediction"
        );

    let uploadedImage =
        localStorage.getItem(
            "uploadedImage"
        );

    let resultText =
        document.getElementById(
            "predictionText"
        );

    let resultImage =
        document.getElementById(
            "uploadedImage"
        );

    if (prediction && resultText) {

        resultText.innerText =
            prediction;

    } else if (resultText) {

        resultText.innerText =
            "No Prediction Available";
    }

    if (uploadedImage && resultImage) {

        resultImage.src =
            uploadedImage;
    }

    analyzeSymptoms();


    // ======================
    // PROFILE PAGE
    // ======================

    let name =
        localStorage.getItem("name");

    let email =
        localStorage.getItem("email");

    let phone =
        localStorage.getItem("phone");

    let sex =
        localStorage.getItem("sex");

    let dob =
        localStorage.getItem("dob");

    let blood =
        localStorage.getItem("blood");

    let country =
        localStorage.getItem("country");

    if (document.getElementById("profileName")) {

        document.getElementById(
            "profileName"
        ).innerText = name || "";

        document.getElementById(
            "profileEmail"
        ).innerText = email || "";

        document.getElementById(
            "profilePhone"
        ).innerText = phone || "";

        document.getElementById(
            "profileSex"
        ).innerText = sex || "";

        document.getElementById(
            "profileDOB"
        ).innerText = dob || "";

        document.getElementById(
            "bloodGroup"
        ).innerText = blood || "";

        document.getElementById(
            "countryName"
        ).innerText = country || "";
    }


    // ======================
    // AGE CALCULATION
    // ======================

    if (dob && document.getElementById("fullAge")) {

        let birthDate =
            new Date(dob);

        let today =
            new Date();

        let years =
            today.getFullYear() -
            birthDate.getFullYear();

        let months =
            today.getMonth() -
            birthDate.getMonth();

        let days =
            today.getDate() -
            birthDate.getDate();

        if (days < 0) {

            months--;
            days += 30;
        }

        if (months < 0) {

            years--;
            months += 12;
        }

        document.getElementById(
            "fullAge"
        ).innerHTML =
            years +
            " Years " +
            months +
            " Months " +
            days +
            " Days Old";
    }


    // ======================
    // PATIENT DETAILS
    // ======================

    let patientName =
        document.getElementById(
            "patientName"
        );

    let patientId =
        document.getElementById(
            "patientId"
        );

    let examDate =
        document.getElementById(
            "examDate"
        );

    if (patientName) {

        patientName.innerText =
            name || "User";
    }

    if (patientId) {

        patientId.innerText =
            localStorage.getItem(
                "patientId"
            );
    }

    if (examDate) {

        examDate.innerText =
            new Date().toDateString();
    }
};