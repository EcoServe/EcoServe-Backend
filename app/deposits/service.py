import datetime as dt
from ..extensions import db
from ..models import Deposit

def add_deposit(user_id, drop_box_id, item_type_id, qty):
    """
    Add a deposit record for a user and store it in the database.
    """
    deposit = Deposit(
        user_id=user_id,
        drop_box_id=drop_box_id,
        item_type_id=item_type_id,
        qty=qty,
        created_at=dt.datetime.utcnow()
    )

    db.session.add(deposit)
    db.session.commit()

    print(f"[DEBUG] Deposit added for user {user_id}, drop_box {drop_box_id}, qty {qty}")
    return deposit, 0  # second return (credits) if your route expects two values
