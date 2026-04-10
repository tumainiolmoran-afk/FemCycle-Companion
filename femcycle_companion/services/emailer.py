from __future__ import annotations

import smtplib
from email.message import EmailMessage
from pathlib import Path

from femcycle_companion.config import BASE_DIR, settings


def send_otp_email(recipient_email: str, otp_code: str) -> tuple[bool, str]:
    subject = "FemCycle Companion Password Reset OTP"
    body = (
        "Your FemCycle Companion password reset code is:\n\n"
        f"{otp_code}\n\n"
        "This code will expire in 10 minutes."
    )

    if not settings.smtp_host or not settings.smtp_username or not settings.smtp_password:
        outbox_path = Path(BASE_DIR) / "otp_outbox.log"
        outbox_path.write_text(
            outbox_path.read_text(encoding="utf-8") + f"\nTo: {recipient_email}\nOTP: {otp_code}\n"
            if outbox_path.exists()
            else f"To: {recipient_email}\nOTP: {otp_code}\n",
            encoding="utf-8",
        )
        return (
            False,
            "Email service is not configured yet. The OTP was written to otp_outbox.log for development.",
        )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_sender_email
    message["To"] = recipient_email
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
        return True, "OTP sent to email successfully."
    except Exception:
        return False, "Could not send OTP by email with the current SMTP settings."
