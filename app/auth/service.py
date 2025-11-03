import random
import datetime as dt
from ..extensions import db
from ..models import AuthOTP, User

# how long the OTP is valid (in minutes)
CODE_TTL_MIN = 10


def issue_code(email, ip):
    """
    Generates a 6-digit OTP code, saves it in the database, and
    (optionally) would send it via email if background jobs were active.
    """
    code = f"{random.randint(0, 999999):06d}"

    otp = AuthOTP(
        email=email,
        code=code,
        expires_at=dt.datetime.utcnow() + dt.timedelta(minutes=CODE_TTL_MIN),
        ip=ip
    )
    db.session.add(otp)
    db.session.commit()

    # ⛔ Disabled for now — requires Redis + RQ worker
    # from ..jobs.tasks import send_email
    # send_email(email, "Your EcoServe code", f"Your code: {code}")

    # For debugging only: print OTP to console/logs
    print(f"[DEBUG] OTP for {email}: {code}")


def verify_code(email, code):
    """
    Verifies the OTP code and returns a user object if valid.
    """
    row = AuthOTP.query.filter_by(email=email, code=code, used_at=None).first()
    if not row or row.expires_at < dt.datetime.utcnow():
        return None

    # Mark OTP as used
    row.used_at = dt.datetime.utcnow()
    db.session.commit()

    # Fetch or create user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, role="student")
        db.session.add(user)
        db.session.commit()

    return user
