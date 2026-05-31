from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)

from app.services.auth_service import AuthService
from app.models.user import User

api_auth_bp = Blueprint("api_auth", __name__)


@api_auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    try:
        user = AuthService.register(data)
        access_token = create_access_token(identity=user.id, additional_claims={"role": user.role.value})
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify({
            "message": "Registration successful",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


@api_auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    try:
        user = AuthService.login(data.get("email", ""), data.get("password", ""))
        access_token = create_access_token(identity=user.id, additional_claims={"role": user.role.value})
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 401


@api_auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user.to_dict()), 200


@api_auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    access_token = create_access_token(identity=user_id, additional_claims={"role": user.role.value})
    return jsonify({"access_token": access_token}), 200
