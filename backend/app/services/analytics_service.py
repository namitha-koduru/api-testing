from sqlalchemy import func

from app.extensions import db
from app.models import (
    Connection,
    ConnectionStatus,
    Event,
    Payment,
    PaymentStatus,
    Poll,
    PollResponse,
    Registration,
    RegistrationStatus,
    SessionAttendance,
    User,
)


class AnalyticsService:
    @staticmethod
    def organizer_dashboard(organizer_id: int) -> dict:
        events = Event.query.filter_by(organizer_id=organizer_id, is_deleted=False).all()
        event_ids = [e.id for e in events]

        registrations = Registration.query.filter(
            Registration.event_id.in_(event_ids),
            Registration.status.in_([RegistrationStatus.CONFIRMED, RegistrationStatus.CHECKED_IN]),
        ).count() if event_ids else 0

        revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.PAID,
            Payment.registration_id.in_(
                db.session.query(Registration.id).filter(Registration.event_id.in_(event_ids))
            ),
        ).scalar() or 0

        checked_in = Registration.query.filter(
            Registration.event_id.in_(event_ids),
            Registration.status == RegistrationStatus.CHECKED_IN,
        ).count() if event_ids else 0

        return {
            "total_events": len(events),
            "total_registrations": registrations,
            "total_revenue": float(revenue),
            "check_ins": checked_in,
            "attendance_rate": round(checked_in / registrations * 100, 1) if registrations else 0,
            "events": [e.to_dict() for e in events],
        }

    @staticmethod
    def platform_admin_dashboard() -> dict:
        return {
            "total_users": User.query.filter_by(is_deleted=False).count(),
            "total_events": Event.query.filter_by(is_deleted=False).count(),
            "total_registrations": Registration.query.filter_by(status=RegistrationStatus.CONFIRMED).count(),
            "total_revenue": float(
                db.session.query(func.sum(Payment.amount)).filter(Payment.status == PaymentStatus.PAID).scalar() or 0
            ),
            "total_connections": Connection.query.filter_by(status=ConnectionStatus.ACCEPTED).count(),
            "active_polls": Poll.query.filter_by(status="active").count(),
            "poll_responses": PollResponse.query.count(),
        }

    @staticmethod
    def event_analytics(event_id: int) -> dict:
        registrations = Registration.query.filter_by(event_id=event_id).count()
        confirmed = Registration.query.filter_by(event_id=event_id, status=RegistrationStatus.CONFIRMED).count()
        checked_in = Registration.query.filter_by(event_id=event_id, status=RegistrationStatus.CHECKED_IN).count()
        revenue = db.session.query(func.sum(Payment.amount)).join(Registration).filter(
            Registration.event_id == event_id,
            Payment.status == PaymentStatus.PAID,
        ).scalar() or 0
        polls = Poll.query.filter_by(event_id=event_id).count()
        poll_votes = PollResponse.query.join(Poll).filter(Poll.event_id == event_id).count()

        return {
            "registrations": registrations,
            "confirmed": confirmed,
            "checked_in": checked_in,
            "revenue": float(revenue),
            "conversion_rate": round(confirmed / registrations * 100, 1) if registrations else 0,
            "polls": polls,
            "poll_votes": poll_votes,
        }
