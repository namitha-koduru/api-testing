from app.extensions import db
from app.models.user import User, UserRole


class AuthService:
    @staticmethod
    def register(data: dict) -> User:
        email = data["email"].strip().lower()
        username = data["username"].strip()
        password = data["password"]

        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")

        if User.query.filter_by(email=email).first():
            raise ValueError("Email is already registered")

        if User.query.filter_by(username=username).first():
            raise ValueError("Username is already taken")

        user = User(
            email=email,
            username=username,
            first_name=data.get("first_name", "").strip() or None,
            last_name=data.get("last_name", "").strip() or None,
            phone=data.get("phone", "").strip() or None,
            role=UserRole.USER,
            is_active=True,
            is_verified=True,  # auto-verify; add email flow later
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def login(email: str, password: str) -> User:
        user = User.query.filter_by(email=email.strip().lower(), is_active=True).first()
        if not user or not user.check_password(password):
            raise ValueError("Invalid email or password")
        return user

    @staticmethod
    def change_password(user: User, old_password: str, new_password: str):
        if not user.check_password(old_password):
            raise ValueError("Current password is incorrect")
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters")
        user.set_password(new_password)
        db.session.commit()

    @staticmethod
    def update_profile(user: User, data: dict) -> User:
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.phone = data.get("phone", user.phone)
        db.session.commit()
        return user
