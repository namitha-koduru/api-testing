from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import UserRole
from app.services.event_service import EventService
from app.utils.helpers import role_required

ns = Namespace("events", description="Event management")

event_model = ns.model("Event", {
    "title": fields.String(required=True),
    "description": fields.String,
    "short_description": fields.String,
    "banner_url": fields.String,
    "event_type": fields.String,
    "venue": fields.String,
    "is_virtual": fields.Boolean,
    "virtual_url": fields.String,
    "start_date": fields.String(required=True),
    "end_date": fields.String(required=True),
    "timezone": fields.String,
    "max_attendees": fields.Integer,
    "ticket_price": fields.Float,
    "currency": fields.String,
    "is_free": fields.Boolean,
    "tags": fields.List(fields.String),
    "community_id": fields.Integer,
})


@ns.route("")
class EventList(Resource):
    def get(self):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search")
        tags = request.args.getlist("tags")
        event_type = request.args.get("event_type")
        status = request.args.get("status")
        return EventService.list_events(page, per_page, status, search, tags, event_type), 200

    @jwt_required()
    @role_required(UserRole.ORGANIZER, UserRole.ADMIN)
    def post(self):
        try:
            event = EventService.create_event(get_jwt_identity(), request.json)
            return event.to_dict(detailed=True), 201
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/<int:event_id>")
class EventDetail(Resource):
    def get(self, event_id):
        try:
            event = EventService.get_event(event_id=event_id)
            data = event.to_dict(detailed=True)
            data["sessions"] = [s.to_dict() for s in event.sessions.filter_by(is_deleted=False)]
            return data, 200
        except ValueError as e:
            return {"message": str(e)}, 404

    @jwt_required()
    def put(self, event_id):
        try:
            event = EventService.update_event(event_id, get_jwt_identity(), request.json)
            return event.to_dict(detailed=True), 200
        except ValueError as e:
            return {"message": str(e)}, 400

    @jwt_required()
    def delete(self, event_id):
        try:
            EventService.delete_event(event_id, get_jwt_identity())
            return {"message": "Event deleted"}, 200
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/<int:event_id>/publish")
class PublishEvent(Resource):
    @jwt_required()
    def post(self, event_id):
        try:
            event = EventService.publish_event(event_id, get_jwt_identity())
            return event.to_dict(), 200
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/<int:event_id>/register")
class RegisterEvent(Resource):
    @jwt_required()
    def post(self, event_id):
        try:
            data = request.json or {}
            registration = EventService.register_for_event(
                get_jwt_identity(), event_id,
                workshop_id=data.get("workshop_id"),
                ticket_type=data.get("ticket_type", "standard"),
            )
            return registration.to_dict(), 201
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/slug/<slug>")
class EventBySlug(Resource):
    def get(self, slug):
        try:
            event = EventService.get_event(slug=slug)
            return event.to_dict(detailed=True), 200
        except ValueError as e:
            return {"message": str(e)}, 404
