# EventNet Database Schema

## ER Diagram

```mermaid
erDiagram
    Users ||--o{ Events : organizes
    Users ||--o{ Registrations : makes
    Users ||--o{ Connections : requests
    Users ||--o{ ChatMessages : sends
    Users ||--o{ Notifications : receives
    Users ||--o{ AIRecommendations : receives
    Users ||--o{ ActivityLogs : generates
    Users ||--o{ Certificates : earns
    Users ||--o{ CommunityMembers : joins
    Users ||--o{ Posts : authors
    Users ||--o{ Comments : writes
    Users ||--o{ PollResponses : votes
    Users ||--o{ Questions : asks

    Events ||--o{ Sessions : contains
    Events ||--o{ Workshops : contains
    Events ||--o{ Registrations : has
    Events ||--o{ EventTags : tagged
    Events ||--o{ Polls : hosts
    Events }o--o| Communities : belongs_to

    Sessions ||--o{ Speakers : features
    Sessions ||--o{ SessionAttendance : tracks
    Sessions ||--o{ Questions : receives
    Sessions ||--o{ Polls : runs

    Workshops ||--o{ Registrations : optional
    Workshops ||--o{ Certificates : issues

    Registrations ||--o| Payments : has

    Communities ||--o{ CommunityMembers : has
    Communities ||--o{ Posts : contains
    Posts ||--o{ Comments : has

    Polls ||--o{ PollResponses : collects
```

## Tables (22)

All tables include `id`, `created_at`, `updated_at`. Soft-delete tables also have `is_deleted`, `deleted_at`.

| # | Table | Key Relationships |
|---|-------|-------------------|
| 1 | users | Central entity |
| 2 | events | FK → users, communities |
| 3 | sessions | FK → events |
| 4 | speakers | FK → sessions |
| 5 | workshops | FK → events |
| 6 | registrations | FK → users, events, workshops |
| 7 | payments | FK → users, registrations |
| 8 | connections | FK → users (requester, receiver) |
| 9 | chat_messages | FK → users, events, sessions |
| 10 | polls | FK → events, sessions, users |
| 11 | poll_responses | FK → polls, users |
| 12 | questions | FK → sessions, users |
| 13 | notifications | FK → users |
| 14 | communities | FK → users (owner) |
| 15 | community_members | FK → communities, users |
| 16 | posts | FK → communities, users |
| 17 | comments | FK → posts, users |
| 18 | session_attendance | FK → sessions, users |
| 19 | certificates | FK → users, workshops, events |
| 20 | event_tags | FK → events |
| 21 | ai_recommendations | FK → users |
| 22 | activity_logs | FK → users, events |

## Migrations

```bash
cd backend
export FLASK_APP=run.py
flask db migrate -m "description"
flask db upgrade
```

## Seed Data

```bash
python seed.py
```

Creates admin, organizer, attendee users and a sample AI Summit 2026 event.
