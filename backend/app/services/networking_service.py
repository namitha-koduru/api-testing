from app.ai.service import AIService
from app.extensions import db
from app.models import ChatMessage, Connection, ConnectionStatus, Notification, NotificationType, User
from app.utils.helpers import log_activity, paginate_query


class NetworkingService:
    @staticmethod
    def send_connection_request(requester_id: int, receiver_id: int, message: str = "") -> Connection:
        if requester_id == receiver_id:
            raise ValueError("Cannot connect with yourself")

        existing = Connection.query.filter(
            ((Connection.requester_id == requester_id) & (Connection.receiver_id == receiver_id))
            | ((Connection.requester_id == receiver_id) & (Connection.receiver_id == requester_id))
        ).first()
        if existing:
            raise ValueError("Connection already exists")

        requester = User.query.get(requester_id)
        receiver = User.query.get(receiver_id)
        score, reasons = AIService.calculate_networking_score(requester, receiver)

        connection = Connection(
            requester_id=requester_id,
            receiver_id=receiver_id,
            message=message,
            networking_score=score,
            match_reasons=reasons,
        )
        db.session.add(connection)

        notification = Notification(
            user_id=receiver_id,
            type=NotificationType.CONNECTION,
            title="New Connection Request",
            message=f"{requester.full_name} wants to connect with you ({score}% match)",
            link=f"/networking/connections/{connection.id}",
        )
        db.session.add(notification)
        db.session.commit()
        log_activity(requester_id, "connection_requested", "connection", connection.id)
        return connection

    @staticmethod
    def respond_to_connection(connection_id: int, user_id: int, accept: bool) -> Connection:
        connection = Connection.query.get(connection_id)
        if not connection or connection.receiver_id != user_id:
            raise ValueError("Connection not found")
        connection.status = ConnectionStatus.ACCEPTED if accept else ConnectionStatus.REJECTED
        db.session.commit()
        return connection

    @staticmethod
    def get_connections(user_id: int, status: str = None):
        query = Connection.query.filter(
            (Connection.requester_id == user_id) | (Connection.receiver_id == user_id)
        )
        if status:
            query = query.filter_by(status=ConnectionStatus(status))
        return [c.to_dict() for c in query.all()]

    @staticmethod
    def get_suggestions(user_id: int, limit: int = 10):
        return AIService.get_matchmaking_recommendations(user_id, limit)

    @staticmethod
    def send_message(sender_id: int, receiver_id: int, content: str,
                     event_id: int = None, session_id: int = None) -> ChatMessage:
        message = ChatMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            event_id=event_id,
            session_id=session_id,
        )
        db.session.add(message)

        notification = Notification(
            user_id=receiver_id,
            type=NotificationType.MESSAGE,
            title="New Message",
            message=content[:100],
            link="/networking/messages",
        )
        db.session.add(notification)
        db.session.commit()
        return message

    @staticmethod
    def get_conversation(user_id: int, other_user_id: int, page=1, per_page=50):
        query = ChatMessage.query.filter(
            ((ChatMessage.sender_id == user_id) & (ChatMessage.receiver_id == other_user_id))
            | ((ChatMessage.sender_id == other_user_id) & (ChatMessage.receiver_id == user_id)),
            ChatMessage.is_deleted == False,
        ).order_by(ChatMessage.created_at.asc())
        result = paginate_query(query, page, per_page)
        result["items"] = [m.to_dict() for m in result["items"]]
        return result
