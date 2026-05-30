from app.extensions import db
from app.models.mixins import TimestampMixin


class Certificate(TimestampMixin, db.Model):
    __tablename__ = "certificates"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workshop_id = db.Column(
        db.Integer,
        db.ForeignKey("workshops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    verification_code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    pdf_url = db.Column(db.String(500), nullable=True)
    qr_data = db.Column(db.Text, nullable=True)
    issued_at = db.Column(db.DateTime, nullable=False)
    metadata_json = db.Column(db.JSON, default=dict)

    user = db.relationship("User")
    workshop = db.relationship("Workshop", back_populates="certificates")
    event = db.relationship("Event")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "workshop_id": self.workshop_id,
            "event_id": self.event_id,
            "certificate_number": self.certificate_number,
            "verification_code": self.verification_code,
            "pdf_url": self.pdf_url,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
        }


class AIRecommendation(TimestampMixin, db.Model):
    __tablename__ = "ai_recommendations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_type = db.Column(db.String(50), nullable=False, index=True)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer, nullable=False, index=True)
    score = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    metadata_json = db.Column(db.JSON, default=dict)
    is_dismissed = db.Column(db.Boolean, default=False)

    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "recommendation_type": self.recommendation_type,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "score": self.score,
            "reason": self.reason,
            "metadata": self.metadata_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ActivityLog(TimestampMixin, db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="SET NULL"), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(50), nullable=True)
    entity_id = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    metadata_json = db.Column(db.JSON, default=dict)

    user = db.relationship("User", back_populates="activity_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "metadata": self.metadata_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
