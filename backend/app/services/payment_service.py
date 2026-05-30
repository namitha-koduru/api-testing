import os
import uuid
from datetime import datetime, timezone

import qrcode
from flask import current_app

from app.ai.service import AIService
from app.extensions import db
from app.models import (
    Certificate,
    Event,
    Notification,
    NotificationType,
    Payment,
    PaymentStatus,
    Registration,
    RegistrationStatus,
    User,
    Workshop,
)
from app.utils.security import generate_qr_token, verify_razorpay_signature


class PaymentService:
    @staticmethod
    def get_client():
        import razorpay
        return razorpay.Client(
            auth=(current_app.config["RAZORPAY_KEY_ID"], current_app.config["RAZORPAY_KEY_SECRET"])
        )

    @staticmethod
    def create_order(user_id: int, registration_id: int, amount: float, currency: str = "INR") -> dict:
        registration = Registration.query.get(registration_id)
        if not registration or registration.user_id != user_id:
            raise ValueError("Registration not found")

        if amount <= 0:
            registration.status = RegistrationStatus.CONFIRMED
            token, expires = generate_qr_token(registration.id, user_id, registration.event_id)
            registration.qr_token = token
            registration.qr_expires_at = expires
            db.session.commit()
            return {"free": True, "registration_id": registration_id}

        client = PaymentService.get_client()
        order = client.order.create({
            "amount": int(amount * 100),
            "currency": currency,
            "receipt": f"reg_{registration_id}_{uuid.uuid4().hex[:8]}",
            "notes": {"registration_id": str(registration_id), "user_id": str(user_id)},
        })

        payment = Payment(
            user_id=user_id,
            registration_id=registration_id,
            razorpay_order_id=order["id"],
            amount=amount,
            currency=currency,
            status=PaymentStatus.CREATED,
        )
        db.session.add(payment)
        db.session.commit()

        return {
            "order_id": order["id"],
            "amount": amount,
            "currency": currency,
            "key_id": current_app.config["RAZORPAY_KEY_ID"],
            "payment_id": payment.id,
        }

    @staticmethod
    def verify_payment(order_id: str, payment_id: str, signature: str) -> Payment:
        if not verify_razorpay_signature(order_id, payment_id, signature):
            raise ValueError("Invalid payment signature")

        payment = Payment.query.filter_by(razorpay_order_id=order_id).first()
        if not payment:
            raise ValueError("Payment not found")

        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = PaymentStatus.PAID
        payment.payment_method = "razorpay"
        payment.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"

        registration = Registration.query.get(payment.registration_id)
        if registration:
            registration.status = RegistrationStatus.CONFIRMED
            token, expires = generate_qr_token(registration.id, payment.user_id, registration.event_id)
            registration.qr_token = token
            registration.qr_expires_at = expires

        notification = Notification(
            user_id=payment.user_id,
            type=NotificationType.PAYMENT,
            title="Payment Successful",
            message=f"Your payment of {payment.currency} {payment.amount} was successful.",
            link=f"/payments/{payment.id}",
        )
        db.session.add(notification)
        db.session.commit()
        return payment

    @staticmethod
    def process_refund(payment_id: int, amount: float = None, reason: str = "") -> Payment:
        payment = Payment.query.get(payment_id)
        if not payment or payment.status != PaymentStatus.PAID:
            raise ValueError("Invalid payment for refund")

        client = PaymentService.get_client()
        refund_amount = int((amount or float(payment.amount)) * 100)
        client.payment.refund(payment.razorpay_payment_id, {"amount": refund_amount})

        payment.refund_amount = amount or payment.amount
        payment.refund_reason = reason
        payment.status = PaymentStatus.REFUNDED
        db.session.commit()
        return payment


class CertificateService:
    @staticmethod
    def generate_certificate(user_id: int, workshop_id: int) -> Certificate:
        from flask import current_app
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        user = User.query.get(user_id)
        workshop = Workshop.query.get(workshop_id)
        if not user or not workshop:
            raise ValueError("User or workshop not found")

        event = Event.query.get(workshop.event_id)
        cert_number = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        verification_code = uuid.uuid4().hex

        description = AIService.generate_certificate_text(user.full_name, workshop.title, event.title)

        upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        pdf_path = os.path.join(upload_dir, f"{cert_number}.pdf")

        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(width / 2, height - 2 * inch, "Certificate of Completion")
        c.setFont("Helvetica", 16)
        c.drawCentredString(width / 2, height - 3 * inch, f"This certifies that")
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(width / 2, height - 3.5 * inch, user.full_name)
        c.setFont("Helvetica", 14)
        c.drawCentredString(width / 2, height - 4.2 * inch, f"has successfully completed")
        c.drawCentredString(width / 2, height - 4.7 * inch, workshop.title)
        c.drawCentredString(width / 2, height - 5.2 * inch, f"at {event.title}")
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(width / 2, 1.5 * inch, description[:200])
        c.drawCentredString(width / 2, 1 * inch, f"Certificate #: {cert_number}")
        c.drawCentredString(width / 2, 0.7 * inch, f"Verify: {verification_code}")
        c.save()

        qr = qrcode.make(verification_code)
        qr_path = os.path.join(upload_dir, f"{cert_number}_qr.png")
        qr.save(qr_path)

        certificate = Certificate(
            user_id=user_id,
            workshop_id=workshop_id,
            event_id=workshop.event_id,
            certificate_number=cert_number,
            verification_code=verification_code,
            pdf_url=pdf_path,
            qr_data=verification_code,
            issued_at=datetime.now(timezone.utc),
            metadata_json={"description": description},
        )
        db.session.add(certificate)
        db.session.commit()
        return certificate

    @staticmethod
    def verify_certificate(code: str) -> Certificate | None:
        return Certificate.query.filter_by(verification_code=code).first()


class QRCheckInService:
    @staticmethod
    def check_in(qr_token: str, scanner_user_id: int) -> Registration:
        from app.utils.security import verify_qr_token

        payload = verify_qr_token(qr_token)
        if not payload:
            raise ValueError("Invalid or expired QR code")

        registration = Registration.query.get(payload["reg_id"])
        if not registration:
            raise ValueError("Registration not found")

        if registration.status == RegistrationStatus.CHECKED_IN:
            raise ValueError("Already checked in")

        if registration.qr_expires_at and registration.qr_expires_at < datetime.now(timezone.utc):
            raise ValueError("QR code expired")

        registration.status = RegistrationStatus.CHECKED_IN
        registration.checked_in_at = datetime.now(timezone.utc)
        db.session.commit()
        return registration
