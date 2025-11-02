from flask import Blueprint, request, jsonify, session
from ..extensions import limiter
from .service import issue_code, verify_code

bp = Blueprint("auth", __name__)

@bp.post("/otp")
@limiter.limit("5/minute; 20/hour")
def otp():
    email = request.json.get("email","").strip().lower()
    if not email or "@" not in email:
        return {"error":"invalid email"}, 400
    issue_code(email, request.remote_addr)
    return {"sent": True}

@bp.post("/verify")
def verify():
    data = request.json or {}
    user = verify_code(data.get("email","").strip().lower(), data.get("code","").strip())
    if not user:
        return {"error":"invalid code"}, 400
    session["uid"] = user.id
    return {"ok": True, "user": {"id": user.id, "email": user.email, "role": user.role}}
