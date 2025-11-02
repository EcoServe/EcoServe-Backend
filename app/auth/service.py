import random, datetime as dt
from ..extensions import db, rq
from ..models import AuthOTP, User

CODE_TTL_MIN = 10

def issue_code(email, ip):
    code = f"{random.randint(0,999999):06d}"
    otp = AuthOTP(email=email, code=code,
                  expires_at=dt.datetime.utcnow()+dt.timedelta(minutes=CODE_TTL_MIN),
                  ip=ip)
    db.session.add(otp); db.session.commit()
    rq.enqueue("app.jobs.tasks.send_email", email, "Your EcoServe code", f"Your code: {code}")

def verify_code(email, code):
    row = AuthOTP.query.filter_by(email=email, code=code, used_at=None).first()
    if not row or row.expires_at < dt.datetime.utcnow():
        return None
    row.used_at = dt.datetime.utcnow(); db.session.commit()
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, role="student")
        db.session.add(user); db.session.commit()
    return user
