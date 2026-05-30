import enum

from app.extensions import db
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class PollStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class Poll(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "polls"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    options = db.Column(db.JSON, nullable=False)
    status = db.Column(db.Enum(PollStatus), default=PollStatus.DRAFT, index=True)
    is_anonymous = db.Column(db.Boolean, default=False)
    allow_multiple = db.Column(db.Boolean, default=False)
    closes_at = db.Column(db.DateTime, nullable=True)

    event = db.relationship("Event", back_populates="polls")
    session = db.relationship("Session", back_populates="polls")
    responses = db.relationship("PollResponse", back_populates="poll", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self, include_results=False):
        data = {
            "id": self.id,
            "event_id": self.event_id,
            "session_id": self.session_id,
            "question": self.question,
            "options": self.options,
            "status": self.status.value if self.status else None,
            "is_anonymous": self.is_anonymous,
            "allow_multiple": self.allow_multiple,
            "closes_at": self.closes_at.isoformat() if self.closes_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_results:
            counts = {i: 0 for i in range(len(self.options or []))}
            for r in self.responses:
                for idx in r.selected_options or []:
                    if idx in counts:
                        counts[idx] += 1
            data["results"] = counts
            data["total_votes"] = self.responses.count()
        return data


class PollResponse(TimestampMixin, db.Model):
    __tablename__ = "poll_responses"

    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("polls.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_options = db.Column(db.JSON, nullable=False)

    poll = db.relationship("Poll", back_populates="responses")
    user = db.relationship("User")

    __table_args__ = (db.UniqueConstraint("poll_id", "user_id", name="uq_poll_user_response"),)


class QuestionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    ANSWERED = "answered"
    REJECTED = "rejected"


class Question(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(QuestionStatus), default=QuestionStatus.PENDING, index=True)
    answer = db.Column(db.Text, nullable=True)
    answered_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    upvotes = db.Column(db.Integer, default=0)
    is_anonymous = db.Column(db.Boolean, default=False)

    session = db.relationship("Session", back_populates="questions")
    user = db.relationship("User", foreign_keys=[user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id if not self.is_anonymous else None,
            "content": self.content,
            "status": self.status.value if self.status else None,
            "answer": self.answer,
            "upvotes": self.upvotes,
            "is_anonymous": self.is_anonymous,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
