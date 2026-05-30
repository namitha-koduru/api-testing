import secrets
from datetime import datetime, timedelta, timezone

from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token

from app.extensions import db
from app.models import Notification, NotificationType, User, UserRole
from app.utils.helpers import generate_token, log_activity


class AuthService:
    @staticmethod
    def register(data: dict) -> tuple[User, str]:
        if User.query.filter_by(email=data["email"], is_deleted=False).first():
            raise ValueError("Email already registered")
        if User.query.filter_by(username=data["username"], is_deleted=False).first():
            raise ValueError("Username already taken")

        user = User(
            email=data["email"],
            username=data["username"],
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            role=UserRole(data.get("role", UserRole.ATTENDEE.value)),
            verification_token=generate_token(),
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()

        log_activity(user.id, "user_registered", "user", user.id)
        return user, user.verification_token

    @staticmethod
    def login(email: str, password: str) -> dict:
        user = User.query.filter_by(email=email, is_deleted=False, is_active=True).first()
        if not user or not user.check_password(password):
            raise ValueError("Invalid credentials")

        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        access_token = create_access_token(identity=user.id, additional_claims={"role": user.role.value})
        refresh_token = create_refresh_token(identity=user.id)

        log_activity(user.id, "user_login", "user", user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(include_private=True),
        }

    @staticmethod
    def verify_email(token: str) -> User:
        user = User.query.filter_by(verification_token=token).first()
        if not user:
            raise ValueError("Invalid verification token")
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        return user

    @staticmethod
    def request_password_reset(email: str) -> str | None:
        user = User.query.filter_by(email=email, is_deleted=False).first()
        if not user:
            return None
        user.reset_token = generate_token()
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.session.commit()
        return user.reset_token

    @staticmethod
    def reset_password(token: str, new_password: str) -> User:
        user = User.query.filter_by(reset_token=token).first()
        if not user or (user.reset_token_expires and user.reset_token_expires < datetime.now(timezone.utc)):
            raise ValueError("Invalid or expired reset token")
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        return user

    @staticmethod
    def google_oauth(user_info: dict) -> dict:
        user = User.query.filter_by(google_id=user_info["sub"]).first()
        if not user:
            user = User.query.filter_by(email=user_info["email"]).first()
            if user:
                user.google_id = user_info["sub"]
            else:
                username = user_info["email"].split("@")[0]
                base_username = username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                user = User(
                    email=user_info["email"],
                    username=username,
                    first_name=user_info.get("given_name"),
                    last_name=user_info.get("family_name"),
                    avatar_url=user_info.get("picture"),
                    google_id=user_info["sub"],
                    is_verified=True,
                    role=UserRole.ATTENDEE,
                )
                user.set_password(secrets.token_urlsafe(32))
                db.session.add(user)

        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        access_token = create_access_token(identity=user.id, additional_claims={"role": user.role.value})
        refresh_token = create_refresh_token(identity=user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(include_private=True),
        }

    @staticmethod
    def refresh_tokens(user_id: int) -> dict:
        user = User.query.get(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found")
        access_token = create_access_token(identity=user.id, additional_claims={"role": user.role.value})
        refresh_token = create_refresh_token(identity=user.id)
        return {"access_token": access_token, "refresh_token": refresh_token}
