from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from db import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(15))
    blood_group = db.Column(db.String(5))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(15))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.user_id)


class DiseasePrediction(db.Model):
    __tablename__ = "disease_predictions"

    prediction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    disease_name = db.Column(db.String(100), nullable=False)
    prediction_result = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, nullable=True)
    risk_level = db.Column(db.String(50), nullable=True)
    form_data = db.Column(db.Text, nullable=True)

    prediction_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("predictions", cascade="all, delete-orphan"))


class ChatbotHistory(db.Model):
    __tablename__ = "chatbot_history"

    chat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)

    chat_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("chat_history", cascade="all, delete-orphan"))


class Report(db.Model):
    __tablename__ = "reports"

    report_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    report_name = db.Column(db.String(100), nullable=False)
    generated_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    report_path = db.Column(db.Text, nullable=False)

    user = db.relationship("User", backref=db.backref("reports", cascade="all, delete-orphan"))


class DiabetesData(db.Model):
    __tablename__ = "diabetes_data"

    diabetes_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    glucose = db.Column(db.Float, nullable=False)
    blood_pressure = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    insulin = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship("User", backref=db.backref("diabetes_records", cascade="all, delete-orphan"))


class HeartDiseaseData(db.Model):
    __tablename__ = "heart_disease_data"

    heart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    cholesterol = db.Column(db.Float, nullable=False)
    blood_pressure = db.Column(db.Float, nullable=False)
    chest_pain = db.Column(db.String(50), nullable=False)
    heart_rate = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship("User", backref=db.backref("heart_records", cascade="all, delete-orphan"))


class KidneyDiseaseData(db.Model):
    __tablename__ = "kidney_disease_data"

    kidney_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    creatinine = db.Column(db.Float, nullable=False)
    bun = db.Column(db.Float, nullable=False)
    albumin = db.Column(db.Float, nullable=False)
    sugar = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship("User", backref=db.backref("kidney_records", cascade="all, delete-orphan"))


class LiverDiseaseData(db.Model):
    __tablename__ = "liver_disease_data"

    liver_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    bilirubin = db.Column(db.Float, nullable=False)
    alt = db.Column(db.Float, nullable=False)
    ast = db.Column(db.Float, nullable=False)
    proteins = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship("User", backref=db.backref("liver_records", cascade="all, delete-orphan"))


class CancerData(db.Model):
    __tablename__ = "cancer_data"

    cancer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    radius_mean = db.Column(db.Float, nullable=False)
    texture_mean = db.Column(db.Float, nullable=False)
    smoothness = db.Column(db.Float, nullable=False)
    compactness = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship("User", backref=db.backref("cancer_records", cascade="all, delete-orphan"))


class ImageUpload(db.Model):
    __tablename__ = "image_uploads"

    image_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    disease_type = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    prediction_result = db.Column(db.String(50), nullable=True)

    user = db.relationship("User", backref=db.backref("image_uploads", cascade="all, delete-orphan"))


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    activity = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(50), nullable=True)
    log_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("audit_logs", cascade="all, delete-orphan"))


class Complaint(db.Model):
    __tablename__ = "complaints"

    complaint_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)

    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="open", nullable=False)
    admin_response = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("complaints", cascade="all, delete-orphan"))


class Doctor(db.Model):
    __tablename__ = "doctors"

    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    consultation_fee = db.Column(db.Integer)
    hospital = db.Column(db.String(200))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    available_days = db.Column(db.String(100))
    bio = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)


class Appointment(db.Model):
    __tablename__ = "appointments"

    appointment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False)

    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default="scheduled")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("appointments", cascade="all, delete-orphan"))
    doctor = db.relationship("Doctor", backref="appointments")
