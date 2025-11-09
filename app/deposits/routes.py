from flask import Blueprint, request, jsonify
from ..extensions import db
from .service import add_deposit

bp = Blueprint("deposits", __name__)

@bp.post("/api/deposits")
def create_deposit():
    data = request.get_json() or {}

    user_id      = data.get("user_id")
    drop_box_id  = data.get("drop_box_id")
    item_type_id = data.get("item_type_id")
    qty          = data.get("qty")

    if not all([user_id, drop_box_id, item_type_id, qty]):
        return jsonify({"error": "missing_fields"}), 400

    dep, credits = add_deposit(user_id, drop_box_id, item_type_id, qty)
    return jsonify({"id": dep.id, "credits": credits}), 201
