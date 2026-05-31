import enum
from datetime import datetime, timezone

from app.extensions import db


class WorkshopStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Workshop(db.Model):
    __tablename__ = "workshops"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    instructor_name = db.Column(db.String(200), nullable=True)
    instructor_bio = db.Column(db.Text, nullable=True)
    venue = db.Column(db.String(300), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, default=50)
    price = db.Column(db.Numeric(10, 2), default=0)
    is_free = db.Column(db.Boolean, default=True)
    status = db.Column(db.Enum(WorkshopStatus), default=WorkshopStatus.UPCOMING)
    banner_url = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(500), nullable=True)  # comma separated
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    registrations = db.relationship("Registration", back_populates="workshop", lazy="dynamic")
    creator = db.relationship("User", foreign_keys=[created_by])

    @property
    def registered_count(self):
        from app.models.registration import RegistrationStatus, RegistrationType
        return self.registrations.filter_by(
            status=RegistrationStatus.CONFIRMED,
            reg_type=RegistrationType.WORKSHOP
        ).count()

    @property
    def available_seats(self):
        return max(0, self.capacity - self.registered_count)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "instructor_name": self.instructor_name,
            "instructor_bio": self.instructor_bio,
            "venue": self.venue,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "capacity": self.capacity,
            "price": float(self.price) if self.price else 0,
            "is_free": self.is_free,
            "status": self.status.value if self.status else None,
            "banner_url": self.banner_url,
            "tags": self.tags,
            "registered_count": self.registered_count,
            "available_seats": self.available_seats,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
