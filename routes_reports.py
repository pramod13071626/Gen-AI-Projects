import os
import uuid
from flask import Blueprint, request, send_file, jsonify
from flask_login import current_user

from reportlab.pdfgen import canvas

from models import Report
from db import db


reports_bp = Blueprint("reports", __name__)


def _current_user_id():
    if current_user.is_authenticated:
        return current_user.user_id
    return None


@reports_bp.route("/reports/generate", methods=["POST"])
def generate_report():
    payload = request.get_json(silent=True) or {}

    disease_name = payload.get("disease_name")
    prediction_result = payload.get("prediction_result")
    confidence_score = payload.get("confidence_score")
    form_data = payload.get("form_data") or {}

    if not disease_name or prediction_result is None:
        return jsonify({"ok": False, "error": "Missing payload"}), 400

    out_dir = os.path.join(os.path.dirname(__file__), "static", "reports")
    os.makedirs(out_dir, exist_ok=True)

    report_id = str(uuid.uuid4())
    pdf_path = os.path.join(out_dir, f"medilife_report_{report_id}.pdf")

    c = canvas.Canvas(pdf_path)
    y = 800
    c.setFont("Helvetica", 14)
    c.drawString(50, y, "Medilife - Disease Prediction Report")

    y -= 40
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Disease: {disease_name}")

    y -= 25
    c.drawString(50, y, f"Result: {prediction_result}")

    y -= 25
    c.drawString(50, y, f"Confidence: {confidence_score}%")

    y -= 35
    c.setFont("Helvetica", 10)
    for k, v in (form_data.items() if isinstance(form_data, dict) else []):
        y -= 15
        c.drawString(50, y, f"{k}: {v}")
        if y < 50:
            break

    c.save()

    row = Report(
        user_id=_current_user_id(),
        report_name=f"{disease_name}_report.pdf",
        report_path=pdf_path,
    )
    db.session.add(row)
    db.session.commit()

    return jsonify({"ok": True, "report_id": row.report_id, "pdf_path": pdf_path})
