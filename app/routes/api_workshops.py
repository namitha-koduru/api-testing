from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.workshop import Workshop
from app.services.registration_service import RegistrationService

api_workshops_bp = Blueprint("api_workshops", __name__)


@api_workshops_bp.route("/", methods=["GET"])
def list_workshops():
    items = Workshop.query.order_by(Workshop.start_time).all()
    return jsonify([w.to_dict() for w in items]), 200


@api_workshops_bp.route("/<int:workshop_id>", methods=["GET"])
def get_workshop(workshop_id):
    from app.extensions import db
    w = db.session.get(Workshop, workshop_id)
    if not w:
        return jsonify({"message": "Workshop not found"}), 404
    return jsonify(w.to_dict()), 200


@api_workshops_bp.route("/<int:workshop_id>/register", methods=["POST"])
@jwt_required()
def register_workshop(workshop_id):
    user_id = get_jwt_identity()
    try:
        reg = RegistrationService.register_for_workshop(user_id, workshop_id)
        event = reg.workshop
        is_free = event.is_free or float(event.price or 0) <= 0
        return jsonify({
            "message": "Registration created",
            "registration": reg.to_dict(),
            "requires_payment": not is_free,
            "amount": float(event.price) if not is_free else 0,
        }), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
