from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.notifications.service import NotificationService

ns = Namespace("notifications", description="Notifications")


@ns.route("")
class NotificationList(Resource):
    @jwt_required()
    def get(self):
        unread_only = request.args.get("unread") == "true"
        return NotificationService.get_user_notifications(get_jwt_identity(), unread_only), 200


@ns.route("/<int:notification_id>/read")
class MarkRead(Resource):
    @jwt_required()
    def post(self, notification_id):
        notification = NotificationService.mark_read(notification_id, get_jwt_identity())
        if not notification:
            return {"message": "Not found"}, 404
        return notification.to_dict(), 200
