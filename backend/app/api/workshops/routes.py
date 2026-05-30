from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Workshop, WorkshopStatus
from app.services.event_service import EventService
from app.utils.helpers import parse_datetime

ns = Namespace("workshops", description="Workshop management")


@ns.route("/event/<int:event_id>")
class EventWorkshops(Resource):
    def get(self, event_id):
        workshops = Workshop.query.filter_by(event_id=event_id, is_deleted=False).all()
        return [w.to_dict() for w in workshops], 200

    @jwt_required()
    def post(self, event_id):
        data = request.json
        workshop = Workshop(
            event_id=event_id,
            title=data["title"],
            description=data.get("description"),
            instructor_name=data.get("instructor_name"),
            start_time=parse_datetime(data["start_time"]),
            end_time=parse_datetime(data["end_time"]),
            capacity=data.get("capacity"),
            price=data.get("price", 0),
            is_free=data.get("is_free", True),
            room=data.get("room"),
            materials_url=data.get("materials_url"),
        )
        db.session.add(workshop)
        db.session.commit()
        return workshop.to_dict(), 201


@ns.route("/<int:workshop_id>")
class WorkshopDetail(Resource):
    def get(self, workshop_id):
        workshop = Workshop.query.filter_by(id=workshop_id, is_deleted=False).first()
        if not workshop:
            return {"message": "Workshop not found"}, 404
        return workshop.to_dict(), 200

    @jwt_required()
    def put(self, workshop_id):
        workshop = Workshop.query.get(workshop_id)
        if not workshop:
            return {"message": "Not found"}, 404
        data = request.json
        for field in ["title", "description", "instructor_name", "capacity", "price", "room", "materials_url"]:
            if field in data:
                setattr(workshop, field, data[field])
        if "start_time" in data:
            workshop.start_time = parse_datetime(data["start_time"])
        if "end_time" in data:
            workshop.end_time = parse_datetime(data["end_time"])
        db.session.commit()
        return workshop.to_dict(), 200
