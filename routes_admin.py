from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func, case

from models import User, DiseasePrediction, ChatbotHistory, Report, Complaint, Appointment, Doctor
from validators import validate_email, validate_phone, validate_name, validate_password, validate_age


admin_bp = Blueprint("admin", __name__, template_folder="templates")


def _require_admin():
    return bool(getattr(current_user, "is_admin", False))


@admin_bp.route("/admin/dashboard")
@login_required
def dashboard():
    if not _require_admin():
        return "Forbidden", 403

    total_users = User.query.count()
    total_predictions = DiseasePrediction.query.count()
    total_chats = ChatbotHistory.query.count()
    total_complaints = Complaint.query.count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    disease_stats = {}
    disease_pos_neg = {}
    disease_counts = DiseasePrediction.query.with_entities(
        DiseasePrediction.disease_name,
        func.count(DiseasePrediction.prediction_id),
        func.sum(case((DiseasePrediction.prediction_result == '1', 1), else_=0)),
        func.sum(case((DiseasePrediction.prediction_result != '1', 1), else_=0))
    ).group_by(DiseasePrediction.disease_name).all()

    for disease, count, pos, neg in disease_counts:
        disease_stats[disease.lower()] = count
        disease_pos_neg[disease.lower()] = {'positive': int(pos or 0), 'negative': int(neg or 0)}

    return render_template(
        "admin/admin_dashboard.html",
        total_users=total_users,
        total_predictions=total_predictions,
        total_chats=total_chats,
        total_complaints=total_complaints,
        recent_users=recent_users,
        disease_stats=disease_stats,
        disease_pos_neg=disease_pos_neg,
        total_doctors=Doctor.query.count(),
        total_appointments=Appointment.query.count(),
        positive_count=DiseasePrediction.query.filter_by(prediction_result='1').count(),
    )


@admin_bp.route("/admin/predictions")
@login_required
def predictions():
    if not _require_admin():
        return "Forbidden", 403

    preds = DiseasePrediction.query.order_by(DiseasePrediction.prediction_date.desc()).all()
    from collections import OrderedDict
    grouped = OrderedDict()
    for p in preds:
        name = p.user.full_name if p.user else 'Anonymous'
        grouped.setdefault(name, []).append(p)

    return render_template("admin/predictions.html", predictions=preds, grouped=grouped)


@admin_bp.route("/admin/users")
@login_required
def users():
    if not _require_admin():
        return "Forbidden", 403

    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/admin/users/add", methods=["POST"])
@login_required
def add_user():
    if not _require_admin():
        return "Forbidden", 403
    from werkzeug.security import generate_password_hash
    name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()
    phone = request.form.get("phone", "").strip()
    age = request.form.get("age")

    for err in [
        validate_name(name),
        validate_email(email),
        validate_password(password),
        validate_phone(phone) if phone else None,
        validate_age(age),
    ]:
        if err:
            flash(err, "error")
            return redirect(url_for("admin.users"))

    if User.query.filter_by(email=email).first():
        flash("Email already exists", "error")
    else:
        user = User(
            full_name=name, email=email,
            password_hash=generate_password_hash(password),
            phone=phone or None,
            age=int(age) if age else None,
            gender=request.form.get("gender", "").strip() or None,
            blood_group=request.form.get("blood_group", "").strip() or None,
            address=request.form.get("address", "").strip() or None,
            emergency_contact=request.form.get("emergency_contact", "").strip() or None,
            is_admin=request.form.get("is_admin") == "on"
        )
        db.session.add(user)
        db.session.commit()
        flash(f"User '{name}' created successfully", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/admin/users/<int:user_id>/edit", methods=["POST"])
@login_required
def edit_user(user_id):
    if not _require_admin():
        return "Forbidden", 403
    user = User.query.get_or_404(user_id)
    name = request.form.get("full_name", user.full_name).strip()
    email = request.form.get("email", user.email).strip().lower()
    phone = request.form.get("phone", "").strip()
    age = request.form.get("age")
    pwd = request.form.get("password", "").strip()

    for err in [
        validate_name(name),
        validate_email(email),
        validate_phone(phone) if phone else None,
        validate_age(age),
        validate_password(pwd) if pwd else None,
    ]:
        if err:
            flash(err, "error")
            return redirect(url_for("admin.users"))

    user.full_name = name
    user.email = email
    user.phone = phone or None
    user.age = int(age) if age else None
    user.gender = request.form.get("gender", "").strip() or None
    user.blood_group = request.form.get("blood_group", "").strip() or None
    user.address = request.form.get("address", "").strip() or None
    user.emergency_contact = request.form.get("emergency_contact", "").strip() or None
    user.is_admin = request.form.get("is_admin") == "on"
    if pwd:
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(pwd)
    db.session.commit()
    flash(f"User '{user.full_name}' updated", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    if not _require_admin():
        return "Forbidden", 403
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Cannot delete admin user", "error")
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.full_name}' deleted", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/admin/doctors")
@login_required
def doctors():
    if not _require_admin():
        return "Forbidden", 403
    all_doctors = Doctor.query.order_by(Doctor.doctor_id.desc()).all()
    return render_template("admin/doctors.html", doctors=all_doctors)


@admin_bp.route("/admin/doctors/add", methods=["POST"])
@login_required
def add_doctor():
    if not _require_admin():
        return "Forbidden", 403
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()

    for err in [
        validate_name(name),
        validate_email(email) if email else None,
        validate_phone(phone) if phone else None,
    ]:
        if err:
            flash(err, "error")
            return redirect(url_for("admin.doctors"))

    doc = Doctor(
        name=name,
        specialization=request.form.get("specialization", "").strip(),
        qualification=request.form.get("qualification", "").strip() or None,
        experience_years=int(request.form.get("experience_years") or 0) or None,
        consultation_fee=int(request.form.get("consultation_fee") or 0) or None,
        hospital=request.form.get("hospital", "").strip() or None,
        phone=phone or None,
        email=email or None,
        available_days=request.form.get("available_days", "").strip() or None,
        bio=request.form.get("bio", "").strip() or None,
        is_active=True
    )
    db.session.add(doc)
    db.session.commit()
    flash(f"Dr. {doc.name} added successfully", "success")
    return redirect(url_for("admin.doctors"))


@admin_bp.route("/admin/doctors/<int:doctor_id>/edit", methods=["POST"])
@login_required
def edit_doctor(doctor_id):
    if not _require_admin():
        return "Forbidden", 403
    doc = Doctor.query.get_or_404(doctor_id)
    name = request.form.get("name", doc.name).strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()

    for err in [
        validate_name(name),
        validate_email(email) if email else None,
        validate_phone(phone) if phone else None,
    ]:
        if err:
            flash(err, "error")
            return redirect(url_for("admin.doctors"))

    doc.name = name
    doc.specialization = request.form.get("specialization", doc.specialization).strip()
    doc.qualification = request.form.get("qualification", "").strip() or None
    doc.experience_years = int(request.form.get("experience_years") or 0) or None
    doc.consultation_fee = int(request.form.get("consultation_fee") or 0) or None
    doc.hospital = request.form.get("hospital", "").strip() or None
    doc.phone = phone or None
    doc.email = email or None
    doc.available_days = request.form.get("available_days", "").strip() or None
    doc.bio = request.form.get("bio", "").strip() or None
    doc.is_active = request.form.get("is_active") == "on"
    db.session.commit()
    flash(f"Dr. {doc.name} updated", "success")
    return redirect(url_for("admin.doctors"))


@admin_bp.route("/admin/doctors/<int:doctor_id>/delete", methods=["POST"])
@login_required
def delete_doctor(doctor_id):
    if not _require_admin():
        return "Forbidden", 403
    doc = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doc)
    db.session.commit()
    flash(f"Dr. {doc.name} deleted", "success")
    return redirect(url_for("admin.doctors"))


@admin_bp.route("/admin/chatlogs")
@login_required
def chatlogs():
    if not _require_admin():
        return "Forbidden", 403
    logs = ChatbotHistory.query.order_by(ChatbotHistory.chat_time.desc()).limit(200).all()
    return render_template("admin/chatlogs.html", logs=logs)


from db import db
from retrain import retrain_all, retrain_status


@admin_bp.route("/admin/retrain", methods=["POST"])
@login_required
def trigger_retrain():
    if not _require_admin():
        return "Forbidden", 403
    from flask import current_app
    started = retrain_all(current_app._get_current_object())
    if started:
        flash("Model retraining started in background", "success")
    else:
        flash("Retraining already in progress", "error")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/retrain/status")
@login_required
def retrain_status_view():
    if not _require_admin():
        return "Forbidden", 403
    from flask import jsonify
    return jsonify(retrain_status)


@admin_bp.route("/admin/complaints")
@login_required
def complaints():
    if not _require_admin():
        return "Forbidden", 403
    all_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(200).all()
    return render_template("admin/complaints.html", complaints=all_complaints)


@admin_bp.route("/admin/complaints/<int:complaint_id>/respond", methods=["POST"])
@login_required
def respond_complaint(complaint_id):
    if not _require_admin():
        return "Forbidden", 403
    ticket = Complaint.query.get_or_404(complaint_id)
    ticket.admin_response = request.form.get("response", "").strip()
    ticket.status = request.form.get("status", ticket.status)
    db.session.commit()
    flash("Response sent successfully", "success")
    return redirect(url_for("admin.complaints"))


@admin_bp.route("/admin/appointments")
@login_required
def admin_appointments():
    if not _require_admin():
        return "Forbidden", 403
    apts = Appointment.query.order_by(Appointment.created_at.desc()).limit(200).all()
    doctors = Doctor.query.filter_by(is_active=True).all()
    return render_template("admin/appointments.html", appointments=apts, doctors=doctors)


@admin_bp.route("/admin/appointments/<int:apt_id>/update", methods=["POST"])
@login_required
def update_appointment(apt_id):
    if not _require_admin():
        return "Forbidden", 403
    apt = Appointment.query.get_or_404(apt_id)
    new_status = request.form.get("status")
    new_date = request.form.get("date")
    new_time = request.form.get("time")
    if new_status:
        apt.status = new_status
    if new_date:
        from datetime import date as date_cls
        apt.appointment_date = date_cls.fromisoformat(new_date)
    if new_time:
        apt.appointment_time = new_time
    db.session.commit()
    flash("Appointment updated", "success")
    return redirect(url_for("admin.admin_appointments"))


@admin_bp.route("/admin/health-overview")
@login_required
def health_overview():
    if not _require_admin():
        return "Forbidden", 403

    disease_stats = db.session.query(
        DiseasePrediction.disease_name,
        func.count(DiseasePrediction.prediction_id),
        func.avg(DiseasePrediction.confidence_score),
        func.sum(case((DiseasePrediction.prediction_result == '1', 1), else_=0))
    ).group_by(DiseasePrediction.disease_name).all()

    recent = DiseasePrediction.query.order_by(DiseasePrediction.prediction_date.desc()).limit(20).all()

    top_users = db.session.query(
        User.full_name, User.email, func.count(DiseasePrediction.prediction_id)
    ).join(DiseasePrediction, User.user_id == DiseasePrediction.user_id
    ).group_by(User.full_name, User.email
    ).order_by(func.count(DiseasePrediction.prediction_id).desc()).limit(10).all()

    return render_template("admin/health_overview.html",
                           disease_stats=disease_stats, recent=recent, top_users=top_users)
