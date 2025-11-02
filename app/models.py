from .extensions import db
from sqlalchemy.dialects.postgresql import JSONB, CITEXT
from sqlalchemy import CheckConstraint, func

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.Text)
    role = db.Column(db.Text, nullable=False, default="student")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class AuthOTP(db.Model):
    __tablename__ = "auth_otp"
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used_at = db.Column(db.DateTime(timezone=True))
    ip = db.Column(db.String(64))

class Campus(db.Model):
    __tablename__ = "campuses"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text)

class DropBox(db.Model):
    __tablename__ = "drop_boxes"
    id = db.Column(db.BigInteger, primary_key=True)
    campus_id = db.Column(db.BigInteger, db.ForeignKey("campuses.id"))
    name = db.Column(db.Text, nullable=False)
    location_note = db.Column(db.Text)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    qr_token = db.Column(db.Text, unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class ItemType(db.Model):
    __tablename__ = "item_types"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    unit = db.Column(db.Text, nullable=False, default="pcs")
    credit_per_unit = db.Column(db.Integer, nullable=False, default=1)
    active = db.Column(db.Boolean, default=True)

class ThresholdRule(db.Model):
    __tablename__ = "threshold_rules"
    id = db.Column(db.BigInteger, primary_key=True)
    drop_box_id = db.Column(db.BigInteger, db.ForeignKey("drop_boxes.id"))
    item_type_id = db.Column(db.BigInteger, db.ForeignKey("item_types.id"))
    threshold_qty = db.Column(db.Integer, nullable=False)

class Deposit(db.Model):
    __tablename__ = "deposits"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    drop_box_id = db.Column(db.BigInteger, db.ForeignKey("drop_boxes.id"))
    item_type_id = db.Column(db.BigInteger, db.ForeignKey("item_types.id"))
    qty = db.Column(db.Integer, nullable=False)
    photo_url = db.Column(db.Text)
    credits_awarded = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    __table_args__ = (CheckConstraint('qty > 0', name='qty_positive'),)

class CreditLedger(db.Model):
    __tablename__ = "credit_ledger"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    delta = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    ref_table = db.Column(db.Text)
    ref_id = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Reward(db.Model):
    __tablename__ = "rewards"
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    cost_credits = db.Column(db.Integer, nullable=False)
    coupon_code = db.Column(db.Text)
    max_redemptions = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime(timezone=True))

class Redemption(db.Model):
    __tablename__ = "redemptions"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    reward_id = db.Column(db.BigInteger, db.ForeignKey("rewards.id"))
    credits_spent = db.Column(db.Integer, nullable=False)
    code_issued = db.Column(db.Text)
    status = db.Column(db.Text, default="issued")
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class RecyclerPartner(db.Model):
    __tablename__ = "recycler_partners"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text)
    phone = db.Column(db.Text)

class PickupBatch(db.Model):
    __tablename__ = "pickup_batches"
    id = db.Column(db.BigInteger, primary_key=True)
    drop_box_id = db.Column(db.BigInteger, db.ForeignKey("drop_boxes.id"))
    item_type_id = db.Column(db.BigInteger, db.ForeignKey("item_types.id"))
    qty = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Text, default="pending")
    threshold_triggered_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    scheduled_for = db.Column(db.DateTime(timezone=True))
    recycler_partner_id = db.Column(db.BigInteger, db.ForeignKey("recycler_partners.id"))
