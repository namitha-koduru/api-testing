from app.ai.provider import get_ai_provider
from app.extensions import db
from app.models import AIRecommendation, Event, Session, User


class AIService:
    SYSTEM_PROMPT = (
        "You are EventNet AI, an intelligent assistant for a digital event networking platform. "
        "Provide helpful, concise, professional responses about events, networking, and sessions."
    )

    @staticmethod
    def chat(user_id: int, message: str, context: str = "") -> str:
        provider = get_ai_provider()
        user = User.query.get(user_id)
        user_context = ""
        if user:
            user_context = f"User: {user.full_name}, Skills: {user.skills}, Interests: {user.interests}"
        prompt = f"{user_context}\nContext: {context}\n\nUser question: {message}"
        return provider.generate(prompt, system=AIService.SYSTEM_PROMPT)

    @staticmethod
    def summarize_event(event_id: int) -> str:
        event = Event.query.get(event_id)
        if not event:
            return "Event not found."
        provider = get_ai_provider()
        sessions = Session.query.filter_by(event_id=event_id, is_deleted=False).all()
        session_info = "\n".join([f"- {s.title}: {s.description or 'No description'}" for s in sessions])
        prompt = (
            f"Summarize this event for attendees:\n"
            f"Title: {event.title}\nDescription: {event.description}\n"
            f"Sessions:\n{session_info}\n"
            f"Provide a compelling 3-paragraph summary."
        )
        return provider.generate(prompt, system=AIService.SYSTEM_PROMPT)

    @staticmethod
    def calculate_networking_score(user1: User, user2: User) -> tuple[float, list[str]]:
        skills1 = set(user1.skills or [])
        skills2 = set(user2.skills or [])
        interests1 = set(user1.interests or [])
        interests2 = set(user2.interests or [])

        skill_overlap = skills1 & skills2
        interest_overlap = interests1 & interests2

        skill_score = len(skill_overlap) / max(len(skills1 | skills2), 1) * 40
        interest_score = len(interest_overlap) / max(len(interests1 | interests2), 1) * 30

        location_score = 15 if user1.location and user1.location == user2.location else 0
        company_score = 15 if user1.company and user1.company == user2.company else 0

        total = min(skill_score + interest_score + location_score + company_score, 100)
        reasons = []
        if skill_overlap:
            reasons.append(f"Shared skills: {', '.join(skill_overlap)}")
        if interest_overlap:
            reasons.append(f"Common interests: {', '.join(interest_overlap)}")
        if location_score:
            reasons.append(f"Same location: {user1.location}")
        if company_score:
            reasons.append(f"Same company: {user1.company}")

        return round(total, 1), reasons

    @staticmethod
    def get_matchmaking_recommendations(user_id: int, limit: int = 10) -> list[dict]:
        user = User.query.get(user_id)
        if not user:
            return []

        candidates = User.query.filter(
            User.id != user_id,
            User.is_deleted == False,
            User.is_active == True,
        ).limit(50).all()

        results = []
        for candidate in candidates:
            score, reasons = AIService.calculate_networking_score(user, candidate)
            if score >= 20:
                results.append({
                    "user": candidate.to_dict(),
                    "score": score,
                    "reasons": reasons,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        for item in results[:limit]:
            rec = AIRecommendation(
                user_id=user_id,
                recommendation_type="matchmaking",
                target_type="user",
                target_id=item["user"]["id"],
                score=item["score"],
                reason="; ".join(item["reasons"]),
            )
            db.session.add(rec)
        db.session.commit()
        return results[:limit]

    @staticmethod
    def recommend_sessions(user_id: int, event_id: int, limit: int = 5) -> list[dict]:
        user = User.query.get(user_id)
        sessions = Session.query.filter_by(event_id=event_id, is_deleted=False).all()
        if not user or not sessions:
            return []

        user_skills = set(user.skills or [])
        user_interests = set(user.interests or [])
        scored = []
        for session in sessions:
            text = f"{session.title} {session.description or ''} {session.track or ''}".lower()
            score = sum(1 for s in user_skills | user_interests if s.lower() in text) * 20
            score = min(score + 10, 100)
            scored.append({"session": session.to_dict(), "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    @staticmethod
    def extract_skills_from_resume(resume_text: str) -> list[str]:
        provider = get_ai_provider()
        prompt = (
            f"Extract technical and professional skills from this resume text. "
            f"Return ONLY a comma-separated list of skills, no other text:\n\n{resume_text[:3000]}"
        )
        response = provider.generate(prompt)
        skills = [s.strip() for s in response.split(",") if s.strip()]
        return skills[:30]

    @staticmethod
    def analyze_profile(user_id: int) -> str:
        user = User.query.get(user_id)
        if not user:
            return "User not found."
        provider = get_ai_provider()
        prompt = (
            f"Analyze this professional profile and provide networking tips:\n"
            f"Name: {user.full_name}\nHeadline: {user.headline}\n"
            f"Bio: {user.bio}\nSkills: {user.skills}\nInterests: {user.interests}\n"
            f"Company: {user.company}\nLocation: {user.location}"
        )
        return provider.generate(prompt, system=AIService.SYSTEM_PROMPT)

    @staticmethod
    def generate_certificate_text(user_name: str, workshop_title: str, event_title: str) -> str:
        provider = get_ai_provider()
        prompt = (
            f"Write a formal certificate description (2 sentences) for {user_name} "
            f"who completed workshop '{workshop_title}' at event '{event_title}'."
        )
        return provider.generate(prompt)

    @staticmethod
    def engagement_insights(event_id: int) -> str:
        from app.models import Poll, PollResponse, Question, Registration

        reg_count = Registration.query.filter_by(event_id=event_id, status="confirmed").count()
        poll_count = Poll.query.filter_by(event_id=event_id).count()
        question_count = Question.query.filter(
            Question.session.has(event_id=event_id)
        ).count()

        provider = get_ai_provider()
        prompt = (
            f"Provide engagement insights for an event with:\n"
            f"- {reg_count} registrations\n- {poll_count} polls\n- {question_count} Q&A questions\n"
            f"Give 3 actionable recommendations to improve engagement."
        )
        return provider.generate(prompt, system=AIService.SYSTEM_PROMPT)
