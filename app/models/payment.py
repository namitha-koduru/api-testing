import enum
from datetime import datetime, timezone

from app.extensions import db


class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    registration_id = db.Column(
        db.Integer, db.ForeignKey("registrations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    razorpay_order_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    razorpay_payment_id = db.Column(db.String(100), unique=True, nullable=True)
    razorpay_signature = db.Column(db.String(300), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default="INR")
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.CREATED, index=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=True)
    failure_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = db.relationship("User", back_populates="payments")
    registration = db.relationship("Registration", back_populates="payment")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "registration_id": self.registration_id,
            "razorpay_order_id": self.razorpay_order_id,
            "razorpay_payment_id": self.razorpay_payment_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "status": self.status.value if self.status else None,
            "invoice_number": self.invoice_number,
            "failure_reason": self.failure_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
