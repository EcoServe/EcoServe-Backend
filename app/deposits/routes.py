from flask import Blueprint, request, jsonify, render_template
from ..extensions import db
from ..models import DropBox, ItemType, Deposit, CreditLedger
from .service import add_deposit

bp = Blueprint("deposits", __name__)

@bp.get("/d/<qr_token>")
def deposit_form(qr_token):
    box = DropBox.query.filter_by(qr_token=qr_token).first_or_404()
    items = ItemType.query.filter_by(active=True).all()
    return render_template("deposit.html", box=box, items=items)

@bp.post("/api/deposits")
def create_deposit():
    data = request.form or request.json
    user_id = int(data.get("user_id", 0))
    drop_box_id = int(data.get("drop_box_id"))
    item_type_id = int(data.get("item_type_id"))
    qty = int(data.get("qty"))
    dep, credits = add_deposit(user_id, drop_box_id)
    return {"id": dep.id, "credits_awarded": credits}
