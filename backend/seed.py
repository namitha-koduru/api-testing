from datetime import datetime, timedelta, timezone

from app import create_app
from app.extensions import db
from app.models import (
    Community,
    CommunityMember,
    CommunityMemberRole,
    Event,
    EventStatus,
    EventTag,
    EventType,
    User,
    UserRole,
    Workshop,
)


def seed_database():
    if User.query.first():
        return

    admin = User(
        email="admin@eventnet.io",
        username="admin",
        first_name="Platform",
        last_name="Admin",
        role=UserRole.ADMIN,
        is_verified=True,
        skills=["management", "events"],
        interests=["technology", "networking"],
    )
    admin.set_password("Admin@123")

    organizer = User(
        email="organizer@eventnet.io",
        username="organizer",
        first_name="Event",
        last_name="Organizer",
        role=UserRole.ORGANIZER,
        is_verified=True,
        headline="Senior Event Manager",
        company="EventNet",
        skills=["event planning", "marketing"],
        interests=["conferences", "startups"],
    )
    organizer.set_password("Organizer@123")

    attendee = User(
        email="attendee@eventnet.io",
        username="attendee",
        first_name="Demo",
        last_name="Attendee",
        role=UserRole.ATTENDEE,
        is_verified=True,
        headline="Software Engineer",
        company="TechCorp",
        skills=["python", "react", "ai"],
        interests=["hackathons", "networking", "workshops"],
    )
    attendee.set_password("Attendee@123")

    db.session.add_all([admin, organizer, attendee])
    db.session.flush()

    community = Community(
        name="Tech Innovators",
        slug="tech-innovators",
        description="A community for tech enthusiasts and innovators",
        owner_id=organizer.id,
        is_public=True,
        member_count=2,
    )
    db.session.add(community)
    db.session.flush()

    db.session.add_all([
        CommunityMember(community_id=community.id, user_id=organizer.id, role=CommunityMemberRole.ADMIN),
        CommunityMember(community_id=community.id, user_id=attendee.id, role=CommunityMemberRole.MEMBER),
    ])

    start = datetime.now(timezone.utc) + timedelta(days=30)
    end = start + timedelta(days=2)

    event = Event(
        title="AI Summit 2026",
        slug="ai-summit-2026",
        description="The premier AI conference featuring industry leaders, hands-on workshops, and networking opportunities.",
        short_description="Explore the future of AI with top experts",
        event_type=EventType.CONFERENCE,
        status=EventStatus.PUBLISHED,
        venue="Bangalore International Convention Centre",
        is_virtual=False,
        start_date=start,
        end_date=end,
        max_attendees=500,
        ticket_price=999,
        currency="INR",
        is_free=False,
        organizer_id=organizer.id,
        community_id=community.id,
    )
    db.session.add(event)
    db.session.flush()

    for tag in ["ai", "machine-learning", "networking", "startup"]:
        db.session.add(EventTag(event_id=event.id, tag=tag))

    workshop = Workshop(
        event_id=event.id,
        title="Building AI Agents with Gemini",
        description="Hands-on workshop on building production AI agents",
        instructor_name="Dr. AI Expert",
        start_time=start + timedelta(hours=10),
        end_time=start + timedelta(hours=14),
        capacity=50,
        price=499,
        is_free=False,
        room="Workshop Hall A",
    )
    db.session.add(workshop)
    db.session.commit()
    print("Seed data created successfully")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_database()
