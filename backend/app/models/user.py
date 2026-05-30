import enum

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class UserRole(str, enum.Enum):
    ATTENDEE = "attendee"
    ORGANIZER = "organizer"
    ADMIN = "admin"


class User(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    headline = db.Column(db.String(255), nullable=True)
    company = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    skills = db.Column(db.JSON, default=list)
    interests = db.Column(db.JSON, default=list)
    resume_url = db.Column(db.String(500), nullable=True)
    linkedin_url = db.Column(db.String(500), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.ATTENDEE, nullable=False, index=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    verification_token = db.Column(db.String(255), nullable=True)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)

    events_organized = db.relationship("Event", back_populates="organizer", lazy="dynamic")
    registrations = db.relationship("Registration", back_populates="user", lazy="dynamic")
    connections_sent = db.relationship(
        "Connection",
        foreign_keys="Connection.requester_id",
        back_populates="requester",
        lazy="dynamic",
    )
    connections_received = db.relationship(
        "Connection",
        foreign_keys="Connection.receiver_id",
        back_populates="receiver",
        lazy="dynamic",
    )
    notifications = db.relationship("Notification", back_populates="user", lazy="dynamic")
    activity_logs = db.relationship("ActivityLog", back_populates="user", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        parts = [p for p in [self.first_name, self.last_name] if p]
        return " ".join(parts) if parts else self.username

    def to_dict(self, include_private=False):
        data = {
            "id": self.id,
            "email": self.email if include_private else None,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "headline": self.headline,
            "company": self.company,
            "location": self.location,
            "skills": self.skills or [],
            "interests": self.interests or [],
            "role": self.role.value if self.role else UserRole.ATTENDEE.value,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_private:
            data["linkedin_url"] = self.linkedin_url
            data["resume_url"] = self.resume_url
        return data
