import enum

from app.extensions import db
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class ConnectionStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class Connection(TimestampMixin, db.Model):
    __tablename__ = "connections"

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(db.Enum(ConnectionStatus), default=ConnectionStatus.PENDING, index=True)
    message = db.Column(db.Text, nullable=True)
    networking_score = db.Column(db.Float, nullable=True)
    match_reasons = db.Column(db.JSON, default=list)

    requester = db.relationship("User", foreign_keys=[requester_id], back_populates="connections_sent")
    receiver = db.relationship("User", foreign_keys=[receiver_id], back_populates="connections_received")

    __table_args__ = (
        db.UniqueConstraint("requester_id", "receiver_id", name="uq_connection_pair"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "requester_id": self.requester_id,
            "receiver_id": self.receiver_id,
            "status": self.status.value if self.status else None,
            "message": self.message,
            "networking_score": self.networking_score,
            "match_reasons": self.match_reasons or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ChatMessage(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    message_type = db.Column(db.String(20), default="direct")

    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "event_id": self.event_id,
            "session_id": self.session_id,
            "content": self.content,
            "is_read": self.is_read,
            "message_type": self.message_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
