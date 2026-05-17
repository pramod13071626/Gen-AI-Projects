import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_prediction_email(user_email, user_name, disease_type, prediction_result, confidence):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    if not sender or not password:
        return False

    result_text = "Positive (At Risk)" if str(prediction_result) == "1" else "Negative (Normal)"
    risk_color = "#c62828" if str(prediction_result) == "1" else "#2e7d32"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden;">
        <div style="background: linear-gradient(135deg, #1a237e, #3498db); color: white; padding: 25px; text-align: center;">
            <h2 style="margin: 0;">Medilife Diagnostic Center</h2>
            <p style="margin: 5px 0 0; opacity: 0.9;">AI-Powered Medical Screening Report</p>
        </div>
        <div style="padding: 30px;">
            <p>Dear <strong>{user_name}</strong>,</p>
            <p>Your <strong>{disease_type.title()}</strong> screening has been completed. Here are your results:</p>
            <div style="background: #f8f9fa; border-left: 4px solid {risk_color}; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <p style="margin: 0;"><strong>Disease:</strong> {disease_type.title()}</p>
                <p style="margin: 8px 0;"><strong>Result:</strong> <span style="color: {risk_color}; font-weight: bold;">{result_text}</span></p>
                <p style="margin: 0;"><strong>Confidence:</strong> {confidence}%</p>
            </div>
            {"<p style='color: #c62828; font-weight: bold;'>⚠️ Your result indicates potential risk. Please consult a healthcare professional immediately.</p>" if str(prediction_result) == "1" else "<p style='color: #2e7d32;'>✅ Your results appear normal. Continue regular health checkups.</p>"}
            <p style="margin-top: 20px;">You can view your full report by logging into your Medilife account.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 12px; color: #666;">This is an automated notification from Medilife Diagnostic Center. This does not constitute medical advice.</p>
        </div>
    </div>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Medilife: Your {disease_type.title()} Screening Results"
        msg["From"] = sender
        msg["To"] = user_email
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, user_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
