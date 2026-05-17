from flask import Blueprint, request, jsonify
from flask_login import current_user

from models import (DiseasePrediction, ChatbotHistory, DiabetesData,
                    HeartDiseaseData, KidneyDiseaseData, LiverDiseaseData,
                    CancerData, ImageUpload, AuditLog)
from db import db


logging_bp = Blueprint("logging_api", __name__)


def _current_user_id():
    if current_user.is_authenticated:
        return current_user.user_id
    return None


def _log_disease_specific(user_id, disease_name, form_data, result):
    if not form_data or not isinstance(form_data, dict):
        return
    try:
        d = disease_name.lower()
        if d == "diabetes":
            db.session.add(DiabetesData(
                user_id=user_id,
                glucose=float(form_data.get("glucose") or form_data.get("Glucose") or 0),
                blood_pressure=float(form_data.get("bloodpressure") or form_data.get("BloodPressure") or 0),
                bmi=float(form_data.get("bmi") or form_data.get("BMI") or 0),
                insulin=float(form_data.get("insulin") or form_data.get("Insulin") or 0),
                age=int(float(form_data.get("age") or form_data.get("Age") or 0)),
                result=str(result),
            ))
        elif d == "heart":
            db.session.add(HeartDiseaseData(
                user_id=user_id,
                cholesterol=float(form_data.get("chol") or form_data.get("cholesterol") or 0),
                blood_pressure=float(form_data.get("trestbps") or form_data.get("blood_pressure") or 0),
                chest_pain=str(form_data.get("cp") or form_data.get("chest_pain") or ""),
                heart_rate=float(form_data.get("thalach") or form_data.get("heart_rate") or 0),
                result=str(result),
            ))
        elif d == "kidney":
            db.session.add(KidneyDiseaseData(
                user_id=user_id,
                creatinine=float(form_data.get("sc") or form_data.get("creatinine") or 0),
                bun=float(form_data.get("bu") or form_data.get("bun") or 0),
                albumin=float(form_data.get("al") or form_data.get("albumin") or 0),
                sugar=float(form_data.get("su") or form_data.get("sugar") or 0),
                result=str(result),
            ))
        elif d == "liver":
            db.session.add(LiverDiseaseData(
                user_id=user_id,
                bilirubin=float(form_data.get("total_bilirubin") or form_data.get("Total_Bilirubin") or 0),
                alt=float(form_data.get("alamine_aminotransferase") or form_data.get("Alamine_Aminotransferase") or 0),
                ast=float(form_data.get("aspartate_aminotransferase") or form_data.get("Aspartate_Aminotransferase") or 0),
                proteins=float(form_data.get("total_proteins") or form_data.get("Total_Protiens") or 0),
                result=str(result),
            ))
        elif d == "cancer":
            db.session.add(CancerData(
                user_id=user_id,
                radius_mean=float(form_data.get("radius_mean") or 0),
                texture_mean=float(form_data.get("texture_mean") or 0),
                smoothness=float(form_data.get("smoothness_mean") or form_data.get("smoothness") or 0),
                compactness=float(form_data.get("compactness_mean") or form_data.get("compactness") or 0),
                result=str(result),
            ))
        elif d in ("malaria", "pneumonia"):
            image_name = form_data.get("image", "")
            if image_name:
                db.session.add(ImageUpload(
                    user_id=user_id,
                    disease_type=d,
                    image_path=image_name,
                    prediction_result=str(result),
                ))
    except Exception as e:
        print(f"Disease-specific logging error ({disease_name}): {e}")


@logging_bp.route("/api/log/prediction", methods=["POST"])
def log_prediction():
    payload = request.get_json(silent=True) or {}

    disease_name = payload.get("disease_name")
    prediction_result = payload.get("prediction_result")
    confidence_score = payload.get("confidence_score")
    risk_level = payload.get("risk_level")
    form_data = payload.get("form_data")

    if not disease_name or prediction_result is None:
        return jsonify({"ok": False, "error": "Missing disease_name or prediction_result"}), 400

    import json
    user_id = _current_user_id()

    row = DiseasePrediction(
        user_id=user_id,
        disease_name=str(disease_name),
        prediction_result=str(prediction_result),
        confidence_score=float(confidence_score) if confidence_score is not None else None,
        risk_level=str(risk_level) if risk_level is not None else None,
        form_data=json.dumps(form_data) if form_data else None,
    )
    db.session.add(row)

    _log_disease_specific(user_id, disease_name, form_data, prediction_result)

    db.session.add(AuditLog(
        user_id=user_id,
        activity=f"Prediction: {disease_name} → {prediction_result}",
        ip_address=request.remote_addr,
    ))

    db.session.commit()

    try:
        if current_user.is_authenticated and current_user.email:
            from email_service import send_prediction_email
            send_prediction_email(
                current_user.email, current_user.full_name,
                disease_name, prediction_result, confidence_score or 0
            )
    except Exception:
        pass

    return jsonify({"ok": True, "prediction_id": row.prediction_id})


@logging_bp.route("/api/log/chat", methods=["POST"])
def log_chat():
    payload = request.get_json(silent=True) or {}

    user_message = payload.get("user_message")
    bot_response = payload.get("bot_response")

    if not user_message or bot_response is None:
        return jsonify({"ok": False, "error": "Missing user_message or bot_response"}), 400

    row = ChatbotHistory(
        user_id=_current_user_id(),
        user_message=str(user_message),
        bot_response=str(bot_response),
    )
    db.session.add(row)
    db.session.commit()
    return jsonify({"ok": True, "chat_id": row.chat_id})
