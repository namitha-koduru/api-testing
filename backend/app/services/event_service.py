from sqlalchemy import or_

from app.extensions import db
from app.models import Event, EventStatus, EventTag, EventType, Registration, RegistrationStatus, Session, Speaker
from app.utils.helpers import generate_slug, log_activity, paginate_query, parse_datetime


class EventService:
    @staticmethod
    def create_event(organizer_id: int, data: dict) -> Event:
        slug = generate_slug(data["title"], Event)
        event = Event(
            title=data["title"],
            slug=slug,
            description=data.get("description"),
            short_description=data.get("short_description"),
            banner_url=data.get("banner_url"),
            event_type=EventType(data.get("event_type", EventType.CONFERENCE.value)),
            status=EventStatus.DRAFT,
            venue=data.get("venue"),
            is_virtual=data.get("is_virtual", False),
            virtual_url=data.get("virtual_url"),
            start_date=parse_datetime(data["start_date"]),
            end_date=parse_datetime(data["end_date"]),
            timezone=data.get("timezone", "UTC"),
            max_attendees=data.get("max_attendees"),
            ticket_price=data.get("ticket_price", 0),
            currency=data.get("currency", "INR"),
            is_free=data.get("is_free", True),
            organizer_id=organizer_id,
            community_id=data.get("community_id"),
        )
        db.session.add(event)
        db.session.flush()

        for tag in data.get("tags", []):
            db.session.add(EventTag(event_id=event.id, tag=tag.lower()))

        db.session.commit()
        log_activity(organizer_id, "event_created", "event", event.id, event.id)
        return event

    @staticmethod
    def update_event(event_id: int, organizer_id: int, data: dict) -> Event:
        event = Event.query.filter_by(id=event_id, is_deleted=False).first()
        if not event:
            raise ValueError("Event not found")
        if event.organizer_id != organizer_id:
            raise ValueError("Not authorized")

        for field in ["title", "description", "short_description", "banner_url", "venue",
                      "virtual_url", "timezone", "max_attendees", "ticket_price", "currency"]:
            if field in data:
                setattr(event, field, data[field])
        if "event_type" in data:
            event.event_type = EventType(data["event_type"])
        if "is_virtual" in data:
            event.is_virtual = data["is_virtual"]
        if "is_free" in data:
            event.is_free = data["is_free"]
        if "start_date" in data:
            event.start_date = parse_datetime(data["start_date"])
        if "end_date" in data:
            event.end_date = parse_datetime(data["end_date"])
        if "tags" in data:
            EventTag.query.filter_by(event_id=event.id).delete()
            for tag in data["tags"]:
                db.session.add(EventTag(event_id=event.id, tag=tag.lower()))

        db.session.commit()
        return event

    @staticmethod
    def publish_event(event_id: int, organizer_id: int) -> Event:
        event = Event.query.get(event_id)
        if not event or event.organizer_id != organizer_id:
            raise ValueError("Event not found")
        event.status = EventStatus.PUBLISHED
        db.session.commit()
        return event

    @staticmethod
    def delete_event(event_id: int, organizer_id: int):
        event = Event.query.get(event_id)
        if not event or event.organizer_id != organizer_id:
            raise ValueError("Event not found")
        event.soft_delete()
        db.session.commit()

    @staticmethod
    def list_events(page=1, per_page=20, status=None, search=None, tags=None, event_type=None):
        query = Event.query.filter_by(is_deleted=False)
        if status:
            query = query.filter_by(status=EventStatus(status))
        else:
            query = query.filter_by(status=EventStatus.PUBLISHED)
        if search:
            query = query.filter(or_(
                Event.title.ilike(f"%{search}%"),
                Event.description.ilike(f"%{search}%"),
            ))
        if event_type:
            query = query.filter_by(event_type=EventType(event_type))
        if tags:
            query = query.join(EventTag).filter(EventTag.tag.in_([t.lower() for t in tags]))
        query = query.order_by(Event.start_date.asc())
        result = paginate_query(query, page, per_page)
        result["items"] = [e.to_dict(detailed=True) for e in result["items"]]
        return result

    @staticmethod
    def get_event(event_id: int = None, slug: str = None) -> Event:
        if slug:
            event = Event.query.filter_by(slug=slug, is_deleted=False).first()
        else:
            event = Event.query.filter_by(id=event_id, is_deleted=False).first()
        if not event:
            raise ValueError("Event not found")
        return event

    @staticmethod
    def register_for_event(user_id: int, event_id: int, workshop_id: int = None, ticket_type: str = "standard"):
        event = Event.query.get(event_id)
        if not event or event.status != EventStatus.PUBLISHED:
            raise ValueError("Event not available")

        existing = Registration.query.filter_by(
            user_id=user_id, event_id=event_id, workshop_id=workshop_id, is_deleted=False
        ).first()
        if existing:
            raise ValueError("Already registered")

        registration = Registration(
            user_id=user_id,
            event_id=event_id,
            workshop_id=workshop_id,
            status=RegistrationStatus.PENDING if not event.is_free else RegistrationStatus.CONFIRMED,
            ticket_type=ticket_type,
        )
        db.session.add(registration)
        db.session.commit()
        log_activity(user_id, "event_registered", "registration", registration.id, event_id)
        return registration

    @staticmethod
    def add_session(event_id: int, data: dict) -> Session:
        session = Session(
            event_id=event_id,
            title=data["title"],
            description=data.get("description"),
            start_time=parse_datetime(data["start_time"]),
            end_time=parse_datetime(data["end_time"]),
            room=data.get("room"),
            track=data.get("track"),
            capacity=data.get("capacity"),
        )
        db.session.add(session)
        db.session.flush()
        for sp in data.get("speakers", []):
            db.session.add(Speaker(
                session_id=session.id,
                name=sp["name"],
                title=sp.get("title"),
                company=sp.get("company"),
                bio=sp.get("bio"),
                avatar_url=sp.get("avatar_url"),
            ))
        db.session.commit()
        return session
