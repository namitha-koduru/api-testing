import uuid
from app.extensions import db
from app.models.registration import Registration, RegistrationStatus, RegistrationType
from app.models.workshop import Workshop
from app.models.meeting import Meeting


class RegistrationService:

    @staticmethod
    def register_for_workshop(user_id: int, workshop_id: int) -> Registration:
        workshop = db.session.get(Workshop, workshop_id)
        if not workshop:
            raise ValueError("Workshop not found")

        if workshop.status.value == "cancelled":
            raise ValueError("This workshop has been cancelled")

        existing = Registration.query.filter_by(
            user_id=user_id, workshop_id=workshop_id, reg_type=RegistrationType.WORKSHOP
        ).filter(Registration.status != RegistrationStatus.CANCELLED).first()
        if existing:
            raise ValueError("You are already registered for this workshop")

        if workshop.available_seats <= 0:
            raise ValueError("No seats available for this workshop")

        status = RegistrationStatus.PENDING
        ticket_code = None

        # Auto-confirm free workshops immediately
        if workshop.is_free or float(workshop.price or 0) <= 0:
            status = RegistrationStatus.CONFIRMED
            ticket_code = f"TKT-{uuid.uuid4().hex[:10].upper()}"

        reg = Registration(
            user_id=user_id,
            workshop_id=workshop_id,
            reg_type=RegistrationType.WORKSHOP,
            status=status,
            ticket_code=ticket_code,
        )
        db.session.add(reg)
        db.session.commit()
        return reg

    @staticmethod
    def register_for_meeting(user_id: int, meeting_id: int) -> Registration:
        meeting = db.session.get(Meeting, meeting_id)
        if not meeting:
            raise ValueError("Meeting not found")

        if meeting.status.value == "cancelled":
            raise ValueError("This meeting has been cancelled")

        existing = Registration.query.filter_by(
            user_id=user_id, meeting_id=meeting_id, reg_type=RegistrationType.MEETING
        ).filter(Registration.status != RegistrationStatus.CANCELLED).first()
        if existing:
            raise ValueError("You are already registered for this meeting")

        if meeting.available_seats <= 0:
            raise ValueError("No seats available for this meeting")

        status = RegistrationStatus.PENDING
        ticket_code = None

        # Auto-confirm free meetings immediately
        if meeting.is_free or float(meeting.price or 0) <= 0:
            status = RegistrationStatus.CONFIRMED
            ticket_code = f"TKT-{uuid.uuid4().hex[:10].upper()}"

        reg = Registration(
            user_id=user_id,
            meeting_id=meeting_id,
            reg_type=RegistrationType.MEETING,
            status=status,
            ticket_code=ticket_code,
        )
        db.session.add(reg)
        db.session.commit()
        return reg

    @staticmethod
    def cancel_registration(user_id: int, registration_id: int) -> Registration:
        reg = Registration.query.filter_by(id=registration_id, user_id=user_id).first()
        if not reg:
            raise ValueError("Registration not found")
        if reg.status == RegistrationStatus.CANCELLED:
            raise ValueError("Registration is already cancelled")
        reg.status = RegistrationStatus.CANCELLED
        db.session.commit()
        return reg

    @staticmethod
    def get_user_registrations(user_id: int):
        return (
            Registration.query
            .filter_by(user_id=user_id)
            .order_by(Registration.created_at.desc())
            .all()
        )
