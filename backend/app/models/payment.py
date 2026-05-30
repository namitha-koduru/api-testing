import enum

from app.extensions import db
from app.models.mixins import TimestampMixin


class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class Payment(TimestampMixin, db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    registration_id = db.Column(
        db.Integer,
        db.ForeignKey("registrations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    razorpay_order_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    razorpay_payment_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    razorpay_signature = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default="INR")
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.CREATED, index=True)
    payment_method = db.Column(db.String(50), nullable=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=True)
    invoice_url = db.Column(db.String(500), nullable=True)
    refund_amount = db.Column(db.Numeric(10, 2), default=0)
    refund_reason = db.Column(db.Text, nullable=True)
    metadata_json = db.Column(db.JSON, default=dict)

    user = db.relationship("User")
    registration = db.relationship("Registration", back_populates="payment")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "registration_id": self.registration_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "status": self.status.value if self.status else None,
            "payment_method": self.payment_method,
            "invoice_number": self.invoice_number,
            "invoice_url": self.invoice_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
