from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import UserRole
from app.services.analytics_service import AnalyticsService
from app.utils.helpers import role_required

ns = Namespace("analytics", description="Analytics dashboards")


@ns.route("/organizer")
class OrganizerDashboard(Resource):
    @jwt_required()
    @role_required(UserRole.ORGANIZER, UserRole.ADMIN)
    def get(self):
        return AnalyticsService.organizer_dashboard(get_jwt_identity()), 200


@ns.route("/admin")
class AdminDashboard(Resource):
    @jwt_required()
    @role_required(UserRole.ADMIN)
    def get(self):
        return AnalyticsService.platform_admin_dashboard(), 200


@ns.route("/event/<int:event_id>")
class EventAnalytics(Resource):
    @jwt_required()
    def get(self, event_id):
        return AnalyticsService.event_analytics(event_id), 200
