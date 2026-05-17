import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from sqlalchemy import func

from models import DiseasePrediction, Complaint, Doctor, Appointment
from db import db
from validators import validate_name, validate_phone, validate_age, validate_password


user_bp = Blueprint("user", __name__, template_folder="templates")


@user_bp.route("/dashboard")
@login_required
def dashboard():
    return redirect(url_for("user.profile"))


@user_bp.route("/profile")
@login_required
def profile():
    return render_template("user/profile.html")


@user_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    full_name = request.form.get("full_name", current_user.full_name).strip()
    phone = (request.form.get("phone") or "").strip()
    age = request.form.get("age")

    # Validate inputs
    for err in [
        validate_name(full_name),
        validate_phone(phone) if phone else None,
        validate_age(age),
    ]:
        if err:
            flash(err, "error")
            return redirect(url_for("user.profile"))

    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()
    if new_password:
        if new_password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("user.profile"))
        err = validate_password(new_password)
        if err:
            flash(err, "error")
            return redirect(url_for("user.profile"))
        current_user.set_password(new_password)

    current_user.full_name = full_name
    current_user.age = age or None
    current_user.gender = request.form.get("gender") or None
    current_user.phone = phone or None
    current_user.blood_group = request.form.get("blood_group") or None
    current_user.address = request.form.get("address") or None
    current_user.emergency_contact = request.form.get("emergency_contact") or None

    db.session.commit()
    flash("Profile updated successfully", "success")
    return redirect(url_for("user.profile"))


@user_bp.route("/profile/delete", methods=["POST"])
@login_required
def delete_account():
    password = request.form.get("password", "")
    if not current_user.check_password(password):
        flash("Incorrect password. Account not deleted.", "error")
        return redirect(url_for("user.profile"))

    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    flash("Your account has been deleted.", "success")
    return redirect(url_for("home"))


@user_bp.route("/history")
@login_required
def history():
    preds = (
        DiseasePrediction.query.filter_by(user_id=current_user.user_id)
        .order_by(DiseasePrediction.prediction_date.desc())
        .limit(50)
        .all()
    )
    return render_template("user/history.html", predictions=preds)


@user_bp.route("/history/<int:prediction_id>")
@login_required
def view_report(prediction_id):
    pred = DiseasePrediction.query.filter_by(
        prediction_id=prediction_id, user_id=current_user.user_id
    ).first_or_404()

    form_data = {}
    if pred.form_data:
        try:
            form_data = json.loads(pred.form_data)
        except Exception:
            pass

    return render_template(
        "predict.html",
        pred=int(pred.prediction_result) if pred.prediction_result.isdigit() else pred.prediction_result,
        confidence=pred.confidence_score or 0,
        disease_type=pred.disease_name,
        form_data=form_data,
    )


@user_bp.route("/support", methods=["GET", "POST"])
@login_required
def support():
    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "other")

        if not subject or not description:
            flash("Subject and description are required", "error")
            return redirect(url_for("user.support"))

        ticket = Complaint(
            user_id=current_user.user_id,
            subject=subject,
            description=description,
            category=category,
        )
        db.session.add(ticket)
        db.session.commit()
        flash("Your ticket has been submitted. We'll get back to you soon!", "success")
        return redirect(url_for("user.support"))

    tickets = Complaint.query.filter_by(user_id=current_user.user_id).order_by(Complaint.created_at.desc()).all()
    return render_template("user/support.html", tickets=tickets)


@user_bp.route("/health-trends")
@login_required
def health_trends():
    preds = DiseasePrediction.query.filter_by(user_id=current_user.user_id).order_by(
        DiseasePrediction.prediction_date.asc()).all()

    if not preds:
        return render_template("user/health_trends.html", chart_data=None)

    dates = [p.prediction_date.strftime('%d %b') for p in preds]
    confidences = [p.confidence_score or 0 for p in preds]

    disease_groups = {}
    for p in preds:
        disease_groups.setdefault(p.disease_name, []).append(p.confidence_score or 0)

    disease_names = list(disease_groups.keys())
    avg_confidences = [round(sum(v)/len(v), 1) for v in disease_groups.values()]
    disease_counts = [len(v) for v in disease_groups.values()]

    chart_data = {
        'dates': dates,
        'confidences': confidences,
        'disease_names': disease_names,
        'avg_confidences': avg_confidences,
        'disease_counts': disease_counts,
    }
    return render_template("user/health_trends.html", chart_data=chart_data)


@user_bp.route("/appointments", methods=["GET", "POST"])
@login_required
def appointments():
    if request.method == "POST":
        from datetime import date as date_cls
        doctor_id = request.form.get("doctor_id")
        apt_date = request.form.get("date")
        apt_time = request.form.get("time")
        reason = request.form.get("reason", "")

        if not doctor_id or not apt_date or not apt_time:
            flash("All fields are required", "error")
        else:
            apt = Appointment(
                user_id=current_user.user_id,
                doctor_id=int(doctor_id),
                appointment_date=date_cls.fromisoformat(apt_date),
                appointment_time=apt_time,
                reason=reason,
            )
            db.session.add(apt)
            db.session.commit()
            flash("Appointment booked successfully!", "success")
        return redirect(url_for("user.appointments"))

    from datetime import date
    doctors = Doctor.query.filter_by(is_active=True).all()
    user_apts = Appointment.query.filter_by(user_id=current_user.user_id).order_by(Appointment.appointment_date.desc()).all()
    return render_template("user/appointments.html", doctors=doctors, appointments=user_apts, today=date.today().isoformat())
