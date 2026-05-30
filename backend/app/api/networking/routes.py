from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.networking_service import NetworkingService

ns = Namespace("networking", description="Networking and messaging")


@ns.route("/connect")
class Connect(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.json
            connection = NetworkingService.send_connection_request(
                get_jwt_identity(), data["receiver_id"], data.get("message", "")
            )
            return connection.to_dict(), 201
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/connections")
class Connections(Resource):
    @jwt_required()
    def get(self):
        status = request.args.get("status")
        return NetworkingService.get_connections(get_jwt_identity(), status), 200


@ns.route("/connections/<int:connection_id>/respond")
class RespondConnection(Resource):
    @jwt_required()
    def post(self, connection_id):
        try:
            accept = request.json.get("accept", True)
            connection = NetworkingService.respond_to_connection(connection_id, get_jwt_identity(), accept)
            return connection.to_dict(), 200
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/suggestions")
class Suggestions(Resource):
    @jwt_required()
    def get(self):
        limit = request.args.get("limit", 10, type=int)
        return NetworkingService.get_suggestions(get_jwt_identity(), limit), 200


@ns.route("/messages")
class Messages(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.json
            message = NetworkingService.send_message(
                get_jwt_identity(),
                data["receiver_id"],
                data["content"],
                data.get("event_id"),
                data.get("session_id"),
            )
            return message.to_dict(), 201
        except ValueError as e:
            return {"message": str(e)}, 400


@ns.route("/messages/<int:user_id>")
class Conversation(Resource):
    @jwt_required()
    def get(self, user_id):
        page = request.args.get("page", 1, type=int)
        return NetworkingService.get_conversation(get_jwt_identity(), user_id, page), 200
