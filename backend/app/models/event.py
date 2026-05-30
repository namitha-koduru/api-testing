import enum

from app.extensions import db
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class EventType(str, enum.Enum):
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    MEETUP = "meetup"
    HACKATHON = "hackathon"
    WEBINAR = "webinar"


class Event(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False, index=True)
    slug = db.Column(db.String(350), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    short_description = db.Column(db.String(500), nullable=True)
    banner_url = db.Column(db.String(500), nullable=True)
    event_type = db.Column(db.Enum(EventType), default=EventType.CONFERENCE, nullable=False)
    status = db.Column(db.Enum(EventStatus), default=EventStatus.DRAFT, nullable=False, index=True)
    venue = db.Column(db.String(300), nullable=True)
    is_virtual = db.Column(db.Boolean, default=False, nullable=False)
    virtual_url = db.Column(db.String(500), nullable=True)
    start_date = db.Column(db.DateTime, nullable=False, index=True)
    end_date = db.Column(db.DateTime, nullable=False, index=True)
    timezone = db.Column(db.String(50), default="UTC")
    max_attendees = db.Column(db.Integer, nullable=True)
    ticket_price = db.Column(db.Numeric(10, 2), default=0)
    currency = db.Column(db.String(3), default="INR")
    is_free = db.Column(db.Boolean, default=True, nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    community_id = db.Column(db.Integer, db.ForeignKey("communities.id"), nullable=True)
    metadata_json = db.Column(db.JSON, default=dict)

    organizer = db.relationship("User", back_populates="events_organized")
    community = db.relationship("Community", back_populates="events")
    sessions = db.relationship("Session", back_populates="event", lazy="dynamic", cascade="all, delete-orphan")
    workshops = db.relationship("Workshop", back_populates="event", lazy="dynamic", cascade="all, delete-orphan")
    registrations = db.relationship("Registration", back_populates="event", lazy="dynamic")
    tags = db.relationship("EventTag", back_populates="event", lazy="dynamic", cascade="all, delete-orphan")
    polls = db.relationship("Poll", back_populates="event", lazy="dynamic")

    def to_dict(self, detailed=False):
        data = {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "short_description": self.short_description,
            "banner_url": self.banner_url,
            "event_type": self.event_type.value if self.event_type else None,
            "status": self.status.value if self.status else None,
            "venue": self.venue,
            "is_virtual": self.is_virtual,
            "virtual_url": self.virtual_url,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "timezone": self.timezone,
            "max_attendees": self.max_attendees,
            "ticket_price": float(self.ticket_price) if self.ticket_price else 0,
            "currency": self.currency,
            "is_free": self.is_free,
            "organizer_id": self.organizer_id,
            "community_id": self.community_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if detailed:
            data["description"] = self.description
            data["tags"] = [t.tag for t in self.tags]
            data["registration_count"] = self.registrations.filter_by(status="confirmed").count()
        return data


class EventTag(TimestampMixin, db.Model):
    __tablename__ = "event_tags"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    tag = db.Column(db.String(100), nullable=False, index=True)

    event = db.relationship("Event", back_populates="tags")

    __table_args__ = (db.UniqueConstraint("event_id", "tag", name="uq_event_tag"),)


class Session(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    room = db.Column(db.String(200), nullable=True)
    track = db.Column(db.String(100), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    is_live = db.Column(db.Boolean, default=False)

    event = db.relationship("Event", back_populates="sessions")
    speakers = db.relationship("Speaker", back_populates="session", lazy="dynamic", cascade="all, delete-orphan")
    attendance = db.relationship("SessionAttendance", back_populates="session", lazy="dynamic")
    questions = db.relationship("Question", back_populates="session", lazy="dynamic")
    polls = db.relationship("Poll", back_populates="session", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "room": self.room,
            "track": self.track,
            "capacity": self.capacity,
            "is_live": self.is_live,
            "speakers": [s.to_dict() for s in self.speakers],
        }


class Speaker(TimestampMixin, db.Model):
    __tablename__ = "speakers"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    company = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    linkedin_url = db.Column(db.String(500), nullable=True)

    session = db.relationship("Session", back_populates="speakers")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "name": self.name,
            "title": self.title,
            "company": self.company,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "linkedin_url": self.linkedin_url,
        }


class SessionAttendance(TimestampMixin, db.Model):
    __tablename__ = "session_attendance"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    joined_at = db.Column(db.DateTime, nullable=True)
    left_at = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, default=0)

    session = db.relationship("Session", back_populates="attendance")
    user = db.relationship("User")

    __table_args__ = (db.UniqueConstraint("session_id", "user_id", name="uq_session_user_attendance"),)
