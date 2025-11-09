# app/deposits/routes.py
from flask import Blueprint, request, jsonify
from ..extensions import db
from .service import add_deposit

bp = Blueprint("deposits", __name__)

@bp.post("/api/deposits")
def create_deposit():
    data = request.get_json(silent=True) or {}

    # required fields
    user_id      = data.get("user_id")
    drop_box_id  = data.get("drop_box_id")
    item_type_id = data.get("item_type_id")
    qty          = data.get("qty")

    # validate presence
    missing = [k for k, v in {
        "user_id": user_id,
        "drop_box_id": drop_box_id,
        "item_type_id": item_type_id,
        "qty": qty
    }.items() if v is None]
    if missing:
        return jsonify({"error": "missing_fields", "fields": missing}), 400

    # validate types
    try:
        user_id      = int(user_id)
        drop_box_id  = int(drop_box_id)
        item_type_id = int(item_type_id)
        qty          = int(qty)
    except (TypeError, ValueError):
        return jsonify({"error": "invalid_types"}), 400

    # create deposit (service expects 4 args)
    dep, credits = add_deposit(user_id, drop_box_id, item_type_id, qty)

    return jsonify({"id": dep.id, "credits": credits}), 201
