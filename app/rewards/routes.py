from flask import Blueprint, request
from ..extensions import db
from ..models import Reward, Redemption, CreditLedger

bp = Blueprint("rewards", __name__)

@bp.get("/rewards")
def list_rewards():
    res = [{"id": r.id, "title": r.title, "cost_credits": r.cost_credits} for r in Reward.query.filter_by(active=True).all()]
    return {"rewards": res}

@bp.post("/redeem")
def redeem():
    data = request.json
    reward = Reward.query.get_or_404(data["reward_id"])
    user_id = int(data["user_id"])
    red = Redemption(user_id=user_id, reward_id=reward.id, credits_spent=reward.cost_credits, code_issued=reward.coupon_code or "CODE")
    db.session.add(red)
    db.session.add(CreditLedger(user_id=user_id, delta=-reward.cost_credits, reason="redeem", ref_table="redemptions", ref_id=red.id))
    db.session.commit()
    return {"id": red.id, "code": red.code_issued}
