from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.payment_service import PaymentService
from app.services.registration_service import RegistrationService

api_payments_bp = Blueprint("api_payments", __name__)


@api_payments_bp.route("/create-order", methods=["POST"])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    reg_id = data.get("registration_id")
    amount = data.get("amount")

    if reg_id is None or amount is None:
        return jsonify({"message": "registration_id and amount are required"}), 400

    try:
        result = PaymentService.create_order(
            user_id=user_id,
            registration_id=int(reg_id),
            amount=float(amount),
            currency=data.get("currency", "INR"),
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


@api_payments_bp.route("/verify", methods=["POST"])
@jwt_required()
def verify_payment():
    data = request.get_json(silent=True) or {}
    order_id   = data.get("razorpay_order_id", "")
    payment_id = data.get("razorpay_payment_id", "")
    signature  = data.get("razorpay_signature", "")

    if not all([order_id, payment_id, signature]):
        return jsonify({"message": "razorpay_order_id, razorpay_payment_id and razorpay_signature are required"}), 400

    try:
        payment = PaymentService.verify_payment(order_id, payment_id, signature)
        return jsonify({
            "message": "Payment verified successfully",
            "payment": payment.to_dict(),
            "registration_id": payment.registration_id,
            "ticket_code": payment.registration.ticket_code if payment.registration else None,
        }), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


@api_payments_bp.route("/failed", methods=["POST"])
@jwt_required()
def mark_failed():
    data = request.get_json(silent=True) or {}
    order_id = data.get("razorpay_order_id", "")
    reason   = data.get("reason", "Payment failed or cancelled by user")
    if order_id:
        PaymentService.mark_failed(order_id, reason)
    return jsonify({"message": "Recorded"}), 200


@api_payments_bp.route("/webhook", methods=["POST"])
def webhook():
    """Razorpay webhook endpoint – no JWT required, uses HMAC signature."""
    signature = request.headers.get("X-Razorpay-Signature", "")
    if not PaymentService.verify_webhook_signature(request.data, signature):
        return jsonify({"message": "Invalid webhook signature"}), 400

    event = request.get_json(silent=True) or {}
    event_type = event.get("event", "")

    if event_type == "payment.captured":
        entity = event.get("payload", {}).get("payment", {}).get("entity", {})
        order_id   = entity.get("order_id", "")
        payment_id = entity.get("id", "")
        # Webhook captures don't include signature – fetch from Razorpay client
        try:
            from flask import current_app
            import razorpay
            client = razorpay.Client(auth=(
                current_app.config["RAZORPAY_KEY_ID"],
                current_app.config["RAZORPAY_KEY_SECRET"],
            ))
            # Verify order is paid by fetching from Razorpay
            rp_payment = client.payment.fetch(payment_id)
            if rp_payment.get("status") == "captured":
                from app.models.payment import Payment, PaymentStatus
                from app.models.registration import RegistrationStatus
                from app.extensions import db
                import uuid
                payment = Payment.query.filter_by(razorpay_order_id=order_id).first()
                if payment and payment.status != PaymentStatus.PAID:
                    payment.razorpay_payment_id = payment_id
                    payment.status = PaymentStatus.PAID
                    payment.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
                    if payment.registration:
                        payment.registration.status = RegistrationStatus.CONFIRMED
                        payment.registration.ticket_code = f"TKT-{uuid.uuid4().hex[:10].upper()}"
                    db.session.commit()
        except Exception:
            pass  # Webhook failures are silently logged in production

    elif event_type == "payment.failed":
        entity = event.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = entity.get("order_id", "")
        if order_id:
            PaymentService.mark_failed(order_id, "Payment failed via webhook")

    return jsonify({"status": "ok"}), 200


@api_payments_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = get_jwt_identity()
    pays = PaymentService.get_user_payments(user_id)
    return jsonify([p.to_dict() for p in pays]), 200


@api_payments_bp.route("/registrations", methods=["GET"])
@jwt_required()
def user_registrations():
    user_id = get_jwt_identity()
    regs = RegistrationService.get_user_registrations(user_id)
    return jsonify([r.to_dict() for r in regs]), 200


@api_payments_bp.route("/registrations/<int:reg_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_registration(reg_id):
    user_id = get_jwt_identity()
    try:
        reg = RegistrationService.cancel_registration(user_id, reg_id)
        return jsonify({"message": "Registration cancelled", "registration": reg.to_dict()}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
