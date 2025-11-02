from flask import Blueprint, request
from ..extensions import db
from ..models import PickupBatch

bp = Blueprint("pickups", __name__)

@bp.get("/pickups")
def list_pickups():
    items = PickupBatch.query.all()
    return {"batches": [{"id": b.id, "status": b.status, "qty": b.qty} for b in items]}

@bp.put("/pickups/<int:bid>")
def update_pickup(bid):
    b = PickupBatch.query.get_or_404(bid)
    data = request.json
    b.status = data.get("status", b.status)
    db.session.commit()
    return {"ok": True}
