from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.ai.service import AIService

ns = Namespace("ai", description="AI-powered features")


@ns.route("/chat")
class AIChat(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.json
            response = AIService.chat(get_jwt_identity(), data["message"], data.get("context", ""))
            return {"response": response}, 200
        except Exception as e:
            return {"message": str(e)}, 500


@ns.route("/summarize/<int:event_id>")
class SummarizeEvent(Resource):
    @jwt_required()
    def get(self, event_id):
        try:
            summary = AIService.summarize_event(event_id)
            return {"summary": summary}, 200
        except Exception as e:
            return {"message": str(e)}, 500


@ns.route("/matchmaking")
class Matchmaking(Resource):
    @jwt_required()
    def get(self):
        limit = request.args.get("limit", 10, type=int)
        return AIService.get_matchmaking_recommendations(get_jwt_identity(), limit), 200


@ns.route("/sessions/<int:event_id>")
class SessionRecommendations(Resource):
    @jwt_required()
    def get(self, event_id):
        limit = request.args.get("limit", 5, type=int)
        return AIService.recommend_sessions(get_jwt_identity(), event_id, limit), 200


@ns.route("/profile-analyze")
class ProfileAnalyze(Resource):
    @jwt_required()
    def get(self):
        try:
            analysis = AIService.analyze_profile(get_jwt_identity())
            return {"analysis": analysis}, 200
        except Exception as e:
            return {"message": str(e)}, 500


@ns.route("/extract-skills")
class ExtractSkills(Resource):
    @jwt_required()
    def post(self):
        try:
            skills = AIService.extract_skills_from_resume(request.json.get("resume_text", ""))
            return {"skills": skills}, 200
        except Exception as e:
            return {"message": str(e)}, 500


@ns.route("/engagement/<int:event_id>")
class EngagementInsights(Resource):
    @jwt_required()
    def get(self, event_id):
        try:
            insights = AIService.engagement_insights(event_id)
            return {"insights": insights}, 200
        except Exception as e:
            return {"message": str(e)}, 500
