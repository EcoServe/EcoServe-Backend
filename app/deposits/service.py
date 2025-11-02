from sqlalchemy import func
from ..extensions import db, rq
from ..models import Deposit, CreditLedger, ThresholdRule, PickupBatch, ItemType, DropBox, User
from ..jobs.tasks import notify_threshold_basic

def add_deposit(user_id, drop_box_id, item_type_id, qty, photo_url=None):
    user = User.query.get(user_id)
    item = ItemType.query.get(item_type_id)
    credits = item.credit_per_unit * qty
    dep = Deposit(user_id=user_id, drop_box_id=drop_box_id, item_type_id=item_type_id,
                  qty=qty, photo_url=photo_url, credits_awarded=credits)
    db.session.add(dep); db.session.flush()
    db.session.add(CreditLedger(user_id=user_id, delta=credits, reason="deposit",
                                ref_table="deposits", ref_id=dep.id))
    db.session.commit()
    _check_threshold(drop_box_id, item_type_id)
    return dep, credits

def _check_threshold(drop_box_id, item_type_id):
    rule = ThresholdRule.query.filter_by(drop_box_id=drop_box_id, item_type_id=item_type_id).first()
    if not rule:
        return
    total = db.session.query(func.coalesce(func.sum(Deposit.qty),0)).filter_by(drop_box_id=drop_box_id, item_type_id=item_type_id).scalar() or 0
    open_exists = db.session.query(PickupBatch.id).filter_by(drop_box_id=drop_box_id, item_type_id=item_type_id).filter(PickupBatch.status.in_(["pending","scheduled"])).first()
    if total >= rule.threshold_qty and not open_exists:
        batch = PickupBatch(drop_box_id=drop_box_id, item_type_id=item_type_id, qty=total, status="pending")
        db.session.add(batch); db.session.commit()
        rq.enqueue("app.jobs.tasks.notify_threshold_basic", drop_box_id, item_type_id, total)
