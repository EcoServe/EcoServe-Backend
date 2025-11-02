from flask import Blueprint, request
from ..extensions import db
from ..models import ItemType, DropBox, ThresholdRule

bp = Blueprint("admin", __name__)

@bp.post("/item-types")
def create_item():
    data = request.json
    it = ItemType(name=data["name"], unit=data.get("unit","pcs"), credit_per_unit=data.get("credit_per_unit",1))
    db.session.add(it); db.session.commit()
    return {"id": it.id}

@bp.post("/drop-boxes")
def create_box():
    data = request.json
    box = DropBox(name=data["name"], campus_id=data.get("campus_id"), qr_token=data["qr_token"])
    db.session.add(box); db.session.commit()
    return {"id": box.id}

@bp.post("/threshold-rules")
def create_rule():
    data = request.json
    r = ThresholdRule(drop_box_id=data["drop_box_id"], item_type_id=data["item_type_id"], threshold_qty=data["threshold_qty"])
    db.session.add(r); db.session.commit()
    return {"id": r.id}
