from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import Payment
from app.services.payment_service import CertificateService, PaymentService, QRCheckInService
from app.utils.security import verify_razorpay_webhook

ns = Namespace("payments", description="Payment operations")


@ns.route("/create-order")
class CreateOrder(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.json
            result = PaymentService.create_order(
                get_jwt_identity(),
                data["registration_id"],
                float(data["amount"]),
                data.get("currency", "INR"),
            )
            return result, 200
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/verify")
class VerifyPayment(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.json
            payment = PaymentService.verify_payment(
                data["razorpay_order_id"],
                data["razorpay_payment_id"],
                data["razorpay_signature"],
            )
            return payment.to_dict(), 200
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/webhook")
class PaymentWebhook(Resource):
    def post(self):
        signature = request.headers.get("X-Razorpay-Signature", "")
        if not verify_razorpay_webhook(request.data, signature):
            return {"message": "Invalid signature"}, 400
        event = request.json
        if event.get("event") == "payment.captured":
            payload = event["payload"]["payment"]["entity"]
            try:
                PaymentService.verify_payment(
                    payload["order_id"],
                    payload["id"],
                    payload.get("signature", ""),
                )
            except ValueError:
                pass
        return {"status": "ok"}, 200


@ns.route("/<int:payment_id>")
class PaymentDetail(Resource):
    @jwt_required()
    def get(self, payment_id):
        payment = Payment.query.get(payment_id)
        if not payment or payment.user_id != get_jwt_identity():
            return {"message": "Not found"}, 404
        return payment.to_dict(), 200


@ns.route("/<int:payment_id>/refund")
class RefundPayment(Resource):
    @jwt_required()
    def post(self, payment_id):
        try:
            data = request.json or {}
            payment = PaymentService.process_refund(
                payment_id,
                data.get("amount"),
                data.get("reason", ""),
            )
            return payment.to_dict(), 200
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/check-in")
class QRCheckIn(Resource):
    @jwt_required()
    def post(self):
        try:
            registration = QRCheckInService.check_in(request.json["qr_token"], get_jwt_identity())
            return registration.to_dict(), 200
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/certificates/generate")
class GenerateCertificate(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.json
            cert = CertificateService.generate_certificate(get_jwt_identity(), data["workshop_id"])
            return cert.to_dict(), 201
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/certificates/verify/<code>")
class VerifyCertificate(Resource):
    def get(self, code):
        cert = CertificateService.verify_certificate(code)
        if not cert:
            return {"message": "Invalid certificate"}, 404
        return cert.to_dict(), 200
