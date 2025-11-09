# app/deposits/service.py
import datetime as dt
from ..extensions import db
from ..models import Deposit

def add_deposit(user_id, drop_box_id, item_type_id, qty):
    deposit = Deposit(
        user_id=user_id,
        drop_box_id=drop_box_id,
        item_type_id=item_type_id,
        qty=qty,
        created_at=dt.datetime.utcnow()
    )
    db.session.add(deposit)
    db.session.commit()
    return deposit, 0  # placeholder for credits if you calculate later
