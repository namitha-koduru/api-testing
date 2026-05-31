from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models.user import User
from app.models.workshop import Workshop
from app.models.meeting import Meeting
from app.models.registration import Registration
from app.models.payment import Payment, PaymentStatus

api_admin_bp = Blueprint("api_admin", __name__)


def _require_admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Admin access required"}), 403
    return None


@api_admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    err = _require_admin()
    if err:
        return err
    return jsonify({
        "users": User.query.count(),
        "workshops": Workshop.query.count(),
        "meetings": Meeting.query.count(),
        "registrations": Registration.query.count(),
        "revenue": float(
            db.session.query(db.func.sum(Payment.amount))
            .filter_by(status=PaymentStatus.PAID)
            .scalar() or 0
        ),
    }), 200


@api_admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    err = _require_admin()
    if err:
        return err
    return jsonify([u.to_dict() for u in User.query.all()]), 200


@api_admin_bp.route("/registrations", methods=["GET"])
@jwt_required()
def list_registrations():
    err = _require_admin()
    if err:
        return err
    regs = Registration.query.order_by(Registration.created_at.desc()).all()
    return jsonify([r.to_dict() for r in regs]), 200


@api_admin_bp.route("/payments", methods=["GET"])
@jwt_required()
def list_payments():
    err = _require_admin()
    if err:
        return err
    pays = Payment.query.order_by(Payment.created_at.desc()).all()
    return jsonify([p.to_dict() for p in pays]), 200
