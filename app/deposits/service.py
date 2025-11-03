import datetime as dt
from ..extensions import db
from ..models import Deposit

def add_deposit(user_id, amount, description=None):
    """
    Add a deposit record for a user and store it in the database.
    """
    deposit = Deposit(
        user_id=user_id,
        amount=amount,
        description=description,
        created_at=dt.datetime.utcnow(),
    )
    db.session.add(deposit)
    db.session.commit()

    # ⛔ Disabled for now — requires Redis + RQ worker
    # from ..jobs.tasks import notify_admin
    # notify_admin(f"New deposit added by user {user_id} for ₹{amount}")

    print(f"[DEBUG] Deposit added for user {user_id}: ₹{amount}")
