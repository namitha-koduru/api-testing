import enum
from datetime import datetime, timezone

from app.extensions import db


class MeetingStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Meeting(db.Model):
    __tablename__ = "meetings"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    organizer_name = db.Column(db.String(200), nullable=True)
    venue = db.Column(db.String(300), nullable=True)
    meeting_link = db.Column(db.String(500), nullable=True)  # for virtual
    is_virtual = db.Column(db.Boolean, default=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, default=100)
    price = db.Column(db.Numeric(10, 2), default=0)
    is_free = db.Column(db.Boolean, default=True)
    status = db.Column(db.Enum(MeetingStatus), default=MeetingStatus.UPCOMING)
    banner_url = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    agenda = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    registrations = db.relationship("Registration", back_populates="meeting", lazy="dynamic")
    creator = db.relationship("User", foreign_keys=[created_by])

    @property
    def registered_count(self):
        from app.models.registration import RegistrationStatus, RegistrationType
        return self.registrations.filter_by(
            status=RegistrationStatus.CONFIRMED,
            reg_type=RegistrationType.MEETING
        ).count()

    @property
    def available_seats(self):
        return max(0, self.capacity - self.registered_count)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "organizer_name": self.organizer_name,
            "venue": self.venue,
            "meeting_link": self.meeting_link,
            "is_virtual": self.is_virtual,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "capacity": self.capacity,
            "price": float(self.price) if self.price else 0,
            "is_free": self.is_free,
            "status": self.status.value if self.status else None,
            "banner_url": self.banner_url,
            "tags": self.tags,
            "agenda": self.agenda,
            "registered_count": self.registered_count,
            "available_seats": self.available_seats,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
