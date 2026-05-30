from flask_restx import Api

from app.api.auth.routes import ns as auth_ns
from app.api.events.routes import ns as events_ns
from app.api.workshops.routes import ns as workshops_ns
from app.api.payments.routes import ns as payments_ns
from app.api.networking.routes import ns as networking_ns
from app.api.analytics.routes import ns as analytics_ns
from app.api.ai.routes import ns as ai_ns
from app.api.polls.routes import ns as polls_ns
from app.api.sessions.routes import ns as sessions_ns
from app.api.notifications.routes import ns as notifications_ns


authorizations = {
    "Bearer": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "JWT Authorization header. Example: Bearer {token}",
    }
}

api = Api(
    title="EventNet API",
    version="1.0",
    description="Digital Event Networking and Interaction Platform API",
    doc="/api/docs",
    prefix="/api",
    authorizations=authorizations,
    security="Bearer",
)

api.add_namespace(auth_ns, path="/auth")
api.add_namespace(events_ns, path="/events")
api.add_namespace(workshops_ns, path="/workshops")
api.add_namespace(payments_ns, path="/payments")
api.add_namespace(networking_ns, path="/networking")
api.add_namespace(analytics_ns, path="/analytics")
api.add_namespace(ai_ns, path="/ai")
api.add_namespace(polls_ns, path="/polls")
api.add_namespace(sessions_ns, path="/sessions")
api.add_namespace(notifications_ns, path="/notifications")
