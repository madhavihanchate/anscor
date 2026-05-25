from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def create_report(
    patient_name,
    prediction,
    confidence,
    hemoglobin
):

    filename = "report.pdf"

    c = canvas.Canvas(
        filename,
        pagesize=letter
    )

    c.setFont("Helvetica-Bold", 20)

    c.drawString(
        180,
        750,
        "ANSCOR-AI REPORT"
    )

    c.setFont("Helvetica", 14)

    c.drawString(
        100,
        680,
        f"Patient Name: {patient_name}"
    )

    c.drawString(
        100,
        650,
        f"Prediction: {prediction}"
    )

    c.drawString(
        100,
        620,
        f"Confidence: {confidence}"
    )

    c.drawString(
        100,
        590,
        f"Hemoglobin: {hemoglobin}"
    )

    c.drawString(
        100,
        540,
        "Recommendation:"
    )

    c.drawString(
        120,
        510,
        "Please consult a healthcare professional."
    )

    c.save()

    return filename