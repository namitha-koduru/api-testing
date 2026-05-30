from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Question, QuestionStatus, Session
from app.services.event_service import EventService

ns = Namespace("sessions", description="Event sessions and Q&A")


@ns.route("/event/<int:event_id>")
class EventSessions(Resource):
    def get(self, event_id):
        sessions = Session.query.filter_by(event_id=event_id, is_deleted=False).all()
        return [s.to_dict() for s in sessions], 200

    @jwt_required()
    def post(self, event_id):
        try:
            session = EventService.add_session(event_id, request.json)
            return session.to_dict(), 201
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/<int:session_id>/questions")
class SessionQuestions(Resource):
    def get(self, session_id):
        questions = Question.query.filter_by(session_id=session_id, is_deleted=False).order_by(Question.upvotes.desc()).all()
        return [q.to_dict() for q in questions], 200

    @jwt_required()
    def post(self, session_id):
        data = request.json
        question = Question(
            session_id=session_id,
            user_id=get_jwt_identity(),
            content=data["content"],
            is_anonymous=data.get("is_anonymous", False),
        )
        db.session.add(question)
        db.session.commit()

        from app.websocket.handlers import emit_new_question
        session = Session.query.get(session_id)
        emit_new_question(session.event_id, session_id, question.to_dict())
        return question.to_dict(), 201


@ns.route("/questions/<int:question_id>/answer")
class AnswerQuestion(Resource):
    @jwt_required()
    def post(self, question_id):
        data = request.json
        question = Question.query.get(question_id)
        if not question:
            return {"message": "Not found"}, 404
        question.answer = data["answer"]
        question.answered_by = get_jwt_identity()
        question.status = QuestionStatus.ANSWERED
        db.session.commit()
        return question.to_dict(), 200


@ns.route("/questions/<int:question_id>/upvote")
class UpvoteQuestion(Resource):
    @jwt_required()
    def post(self, question_id):
        question = Question.query.get(question_id)
        if not question:
            return {"message": "Not found"}, 404
        question.upvotes += 1
        db.session.commit()
        return question.to_dict(), 200
