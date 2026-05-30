from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Poll, PollResponse, PollStatus

ns = Namespace("polls", description="Live polls")


@ns.route("")
class PollList(Resource):
    @jwt_required()
    def post(self):
        data = request.json
        poll = Poll(
            event_id=data.get("event_id"),
            session_id=data.get("session_id"),
            created_by=get_jwt_identity(),
            question=data["question"],
            options=data["options"],
            status=PollStatus(data.get("status", "draft")),
            is_anonymous=data.get("is_anonymous", False),
            allow_multiple=data.get("allow_multiple", False),
        )
        db.session.add(poll)
        db.session.commit()
        return poll.to_dict(), 201


@ns.route("/event/<int:event_id>")
class EventPolls(Resource):
    def get(self, event_id):
        polls = Poll.query.filter_by(event_id=event_id, is_deleted=False).all()
        return [p.to_dict(include_results=True) for p in polls], 200


@ns.route("/<int:poll_id>/vote")
class VotePoll(Resource):
    @jwt_required()
    def post(self, poll_id):
        data = request.json
        existing = PollResponse.query.filter_by(poll_id=poll_id, user_id=get_jwt_identity()).first()
        if existing:
            return {"message": "Already voted"}, 400
        response = PollResponse(
            poll_id=poll_id,
            user_id=get_jwt_identity(),
            selected_options=data["selected_options"],
        )
        db.session.add(response)
        db.session.commit()

        poll = Poll.query.get(poll_id)
        from app.websocket.handlers import emit_poll_update
        emit_poll_update(poll.event_id, poll.session_id, poll.to_dict(include_results=True))
        return poll.to_dict(include_results=True), 200


@ns.route("/<int:poll_id>/activate")
class ActivatePoll(Resource):
    @jwt_required()
    def post(self, poll_id):
        poll = Poll.query.get(poll_id)
        if not poll:
            return {"message": "Not found"}, 404
        poll.status = PollStatus.ACTIVE
        db.session.commit()
        from app.websocket.handlers import emit_poll_update
        emit_poll_update(poll.event_id, poll.session_id, poll.to_dict(include_results=True))
        return poll.to_dict(), 200
