import hashlib
import hmac as _hmac
import uuid
from flask import current_app

from app.extensions import db
from app.models.payment import Payment, PaymentStatus
from app.models.registration import Registration, RegistrationStatus


class PaymentService:

    @staticmethod
    def get_razorpay_client():
        import razorpay
        key_id = current_app.config.get("RAZORPAY_KEY_ID", "")
        key_secret = current_app.config.get("RAZORPAY_KEY_SECRET", "")
        if not key_id or not key_secret:
            raise ValueError(
                "Razorpay credentials not configured. "
                "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in your .env file."
            )
        return razorpay.Client(auth=(key_id, key_secret))

    @staticmethod
    def create_order(user_id: int, registration_id: int, amount: float, currency: str = "INR") -> dict:
        registration = db.session.get(Registration, registration_id)
        if not registration or registration.user_id != user_id:
            raise ValueError("Registration not found")

        if registration.status == RegistrationStatus.CONFIRMED:
            raise ValueError("Registration is already confirmed")

        # Guard: if somehow amount is 0, auto-confirm
        if amount <= 0:
            ticket_code = f"TKT-{uuid.uuid4().hex[:10].upper()}"
            registration.status = RegistrationStatus.CONFIRMED
            registration.ticket_code = ticket_code
            db.session.commit()
            return {
                "free": True,
                "registration_id": registration_id,
                "ticket_code": ticket_code,
            }

        client = PaymentService.get_razorpay_client()
        receipt = f"reg_{registration_id}_{uuid.uuid4().hex[:6]}"
        rp_order = client.order.create({
            "amount": int(amount * 100),   # convert to paise
            "currency": currency,
            "receipt": receipt,
            "notes": {
                "registration_id": str(registration_id),
                "user_id": str(user_id),
            },
        })

        payment = Payment(
            user_id=user_id,
            registration_id=registration_id,
            razorpay_order_id=rp_order["id"],
            amount=amount,
            currency=currency,
            status=PaymentStatus.CREATED,
        )
        db.session.add(payment)
        db.session.commit()

        return {
            "order_id": rp_order["id"],
            "amount": int(amount * 100),
            "currency": currency,
            "key_id": current_app.config["RAZORPAY_KEY_ID"],
            "payment_db_id": payment.id,
            "registration_id": registration_id,
        }

    @staticmethod
    def verify_payment(order_id: str, payment_id: str, signature: str) -> Payment:
        """Cryptographically verify Razorpay signature then confirm registration."""
        key_secret = current_app.config.get("RAZORPAY_KEY_SECRET", "")
        msg = f"{order_id}|{payment_id}".encode("utf-8")
        expected = _hmac.new(
            key_secret.encode("utf-8"),
            msg,
            hashlib.sha256,
        ).hexdigest()

        if not _hmac.compare_digest(expected, signature):
            raise ValueError("Payment signature verification failed")

        payment = Payment.query.filter_by(razorpay_order_id=order_id).first()
        if not payment:
            raise ValueError("Payment record not found for this order")

        # Idempotent: already paid
        if payment.status == PaymentStatus.PAID:
            return payment

        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = PaymentStatus.PAID
        payment.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"

        if payment.registration:
            payment.registration.status = RegistrationStatus.CONFIRMED
            payment.registration.ticket_code = f"TKT-{uuid.uuid4().hex[:10].upper()}"

        db.session.commit()
        return payment

    @staticmethod
    def mark_failed(order_id: str, reason: str = "Payment failed or cancelled") -> None:
        payment = Payment.query.filter_by(razorpay_order_id=order_id).first()
        if payment and payment.status in (PaymentStatus.CREATED, PaymentStatus.PENDING):
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = reason
            db.session.commit()

    @staticmethod
    def verify_webhook_signature(body: bytes, signature: str) -> bool:
        secret = current_app.config.get("RAZORPAY_WEBHOOK_SECRET", "")
        if not secret:
            return False
        expected = _hmac.new(
            secret.encode("utf-8"), body, hashlib.sha256
        ).hexdigest()
        return _hmac.compare_digest(expected, signature)

    @staticmethod
    def get_user_payments(user_id: int):
        return (
            Payment.query
            .filter_by(user_id=user_id)
            .order_by(Payment.created_at.desc())
            .all()
        )
