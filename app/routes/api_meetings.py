from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.meeting import Meeting
from app.services.registration_service import RegistrationService

api_meetings_bp = Blueprint("api_meetings", __name__)


@api_meetings_bp.route("/", methods=["GET"])
def list_meetings():
    items = Meeting.query.order_by(Meeting.start_time).all()
    return jsonify([m.to_dict() for m in items]), 200


@api_meetings_bp.route("/<int:meeting_id>", methods=["GET"])
def get_meeting(meeting_id):
    from app.extensions import db
    m = db.session.get(Meeting, meeting_id)
    if not m:
        return jsonify({"message": "Meeting not found"}), 404
    return jsonify(m.to_dict()), 200


@api_meetings_bp.route("/<int:meeting_id>/register", methods=["POST"])
@jwt_required()
def register_meeting(meeting_id):
    user_id = get_jwt_identity()
    try:
        reg = RegistrationService.register_for_meeting(user_id, meeting_id)
        event = reg.meeting
        is_free = event.is_free or float(event.price or 0) <= 0
        return jsonify({
            "message": "Registration created",
            "registration": reg.to_dict(),
            "requires_payment": not is_free,
            "amount": float(event.price) if not is_free else 0,
        }), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
