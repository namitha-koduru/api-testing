from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService

ns = Namespace("auth", description="Authentication operations")

register_model = ns.model("Register", {
    "email": fields.String(required=True),
    "username": fields.String(required=True),
    "password": fields.String(required=True),
    "first_name": fields.String,
    "last_name": fields.String,
    "role": fields.String(enum=["attendee", "organizer"]),
})

login_model = ns.model("Login", {
    "email": fields.String(required=True),
    "password": fields.String(required=True),
})


@ns.route("/register")
class Register(Resource):
    @ns.expect(register_model)
    def post(self):
        try:
            user, token = AuthService.register(request.json)
            return {"message": "Registration successful", "user": user.to_dict(), "verification_token": token}, 201
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/login")
class Login(Resource):
    @ns.expect(login_model)
    def post(self):
        try:
            data = request.json
            result = AuthService.login(data["email"], data["password"])
            return result, 200
        except ValueError as e:
            return {"message": str(e)}, 401


@ns.route("/verify-email/<token>")
class VerifyEmail(Resource):
    def get(self, token):
        try:
            user = AuthService.verify_email(token)
            return {"message": "Email verified", "user": user.to_dict()}, 200
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/forgot-password")
class ForgotPassword(Resource):
    def post(self):
        email = request.json.get("email")
        token = AuthService.request_password_reset(email)
        return {"message": "If email exists, reset link sent", "reset_token": token}, 200


@ns.route("/reset-password")
class ResetPassword(Resource):
    def post(self):
        try:
            data = request.json
            user = AuthService.reset_password(data["token"], data["password"])
            return {"message": "Password reset successful", "user": user.to_dict()}, 200
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/refresh")
class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        try:
            user_id = get_jwt_identity()
            tokens = AuthService.refresh_tokens(user_id)
            return tokens, 200
        except ValueError as e:
            return {"message": str(e)}, 401


@ns.route("/google")
class GoogleOAuth(Resource):
    def post(self):
        try:
            result = AuthService.google_oauth(request.json)
            return result, 200
        except Exception as e:
            return {"message": str(e)}, 400


@ns.route("/me")
class Me(Resource):
    @jwt_required()
    def get(self):
        from app.models import User
        user = User.query.get(get_jwt_identity())
        if not user:
            return {"message": "User not found"}, 404
        return user.to_dict(include_private=True), 200
