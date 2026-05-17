from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from models import User, AuditLog
from db import db
from auth import is_admin
from validators import validate_email, validate_phone, validate_name, validate_password, validate_age


auth_bp = Blueprint("auth", __name__, template_folder="templates")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        err = validate_email(email)
        if err:
            flash(err, "error")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid credentials", "error")
            return redirect(url_for("auth.login"))

        login_user(user)

        db.session.add(AuditLog(user_id=user.user_id, activity="Login", ip_address=request.remote_addr))
        db.session.commit()

        if user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("home"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        phone = (request.form.get("phone") or "").strip()
        age = request.form.get("age")

        # Validate all fields
        for err in [
            validate_name(full_name),
            validate_email(email),
            validate_password(password),
            validate_phone(phone) if phone else None,
            validate_age(age),
        ]:
            if err:
                flash(err, "error")
                return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return redirect(url_for("auth.register"))

        user = User(full_name=full_name, email=email)
        user.set_password(password)

        user.age = age
        user.gender = request.form.get("gender")
        user.phone = phone or None
        user.blood_group = request.form.get("blood_group")
        user.address = request.form.get("address")
        user.emergency_contact = request.form.get("emergency_contact")

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    db.session.add(AuditLog(user_id=current_user.user_id, activity="Logout", ip_address=request.remote_addr))
    db.session.commit()
    logout_user()
    return redirect(url_for("home"))


@auth_bp.route("/admin")
@login_required
def admin_home():
    if not is_admin():
        flash("Admin access required", "error")
        return redirect(url_for("home"))
    return redirect(url_for("admin.dashboard"))
