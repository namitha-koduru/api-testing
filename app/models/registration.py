import enum
from datetime import datetime, timezone

from app.extensions import db


class RegistrationStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class RegistrationType(str, enum.Enum):
    WORKSHOP = "workshop"
    MEETING = "meeting"


class Registration(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workshop_id = db.Column(db.Integer, db.ForeignKey("workshops.id", ondelete="CASCADE"), nullable=True, index=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=True, index=True)
    reg_type = db.Column(db.Enum(RegistrationType), nullable=False)
    status = db.Column(db.Enum(RegistrationStatus), default=RegistrationStatus.PENDING, index=True)
    ticket_code = db.Column(db.String(50), unique=True, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = db.relationship("User", back_populates="registrations")
    workshop = db.relationship("Workshop", back_populates="registrations")
    meeting = db.relationship("Meeting", back_populates="registrations")
    payment = db.relationship("Payment", back_populates="registration", uselist=False)

    @property
    def event_title(self):
        if self.workshop:
            return self.workshop.title
        if self.meeting:
            return self.meeting.title
        return "Unknown"

    @property
    def event_start_time(self):
        if self.workshop:
            return self.workshop.start_time
        if self.meeting:
            return self.meeting.start_time
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "workshop_id": self.workshop_id,
            "meeting_id": self.meeting_id,
            "reg_type": self.reg_type.value if self.reg_type else None,
            "status": self.status.value if self.status else None,
            "ticket_code": self.ticket_code,
            "event_title": self.event_title,
            "event_start_time": self.event_start_time.isoformat() if self.event_start_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
