import os, smtplib
from email.message import EmailMessage

def _smtp_params():
    # Very simple SMTP sender parsing (expects: smtp+tls://user:pass@host:587)
    url = os.getenv("SMTP_URL","")
    return url

def send_email(to, subject, body):
    # NOTE: Simplified. Replace with robust SMTP settings in production.
    msg = EmailMessage()
    msg["To"] = to
    msg["From"] = "no-reply@ecoserve.local"
    msg["Subject"] = subject
    msg.set_content(body)
    # For demo purposes we just print instead of sending
    print(f"[EMAIL] To:{to} Subject:{subject}\n{body}")

def notify_threshold_basic(drop_box_id, item_type_id, qty):
    send_email("admin@example.com", "Pickup threshold reached", f"Box {drop_box_id}, item {item_type_id}, qty {qty}")
