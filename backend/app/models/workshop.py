import enum

from app.extensions import db
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class WorkshopStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Workshop(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "workshops"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    instructor_name = db.Column(db.String(200), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Numeric(10, 2), default=0)
    is_free = db.Column(db.Boolean, default=True)
    status = db.Column(db.Enum(WorkshopStatus), default=WorkshopStatus.SCHEDULED)
    room = db.Column(db.String(200), nullable=True)
    materials_url = db.Column(db.String(500), nullable=True)

    event = db.relationship("Event", back_populates="workshops")
    registrations = db.relationship("Registration", back_populates="workshop", lazy="dynamic")
    certificates = db.relationship("Certificate", back_populates="workshop", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "instructor_name": self.instructor_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "capacity": self.capacity,
            "price": float(self.price) if self.price else 0,
            "is_free": self.is_free,
            "status": self.status.value if self.status else None,
            "room": self.room,
            "materials_url": self.materials_url,
        }


class RegistrationStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"


class Registration(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    workshop_id = db.Column(db.Integer, db.ForeignKey("workshops.id", ondelete="SET NULL"), nullable=True, index=True)
    status = db.Column(db.Enum(RegistrationStatus), default=RegistrationStatus.PENDING, index=True)
    qr_token = db.Column(db.String(500), nullable=True, unique=True)
    qr_expires_at = db.Column(db.DateTime, nullable=True)
    checked_in_at = db.Column(db.DateTime, nullable=True)
    is_bookmarked = db.Column(db.Boolean, default=False)
    ticket_type = db.Column(db.String(50), default="standard")
    notes = db.Column(db.Text, nullable=True)

    user = db.relationship("User", back_populates="registrations")
    event = db.relationship("Event", back_populates="registrations")
    workshop = db.relationship("Workshop", back_populates="registrations")
    payment = db.relationship("Payment", back_populates="registration", uselist=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "event_id", "workshop_id", name="uq_user_event_workshop_reg"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "workshop_id": self.workshop_id,
            "status": self.status.value if self.status else None,
            "checked_in_at": self.checked_in_at.isoformat() if self.checked_in_at else None,
            "is_bookmarked": self.is_bookmarked,
            "ticket_type": self.ticket_type,
            "has_qr": bool(self.qr_token),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
