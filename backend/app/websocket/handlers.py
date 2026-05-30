from flask_jwt_extended import decode_token
from flask_socketio import emit, join_room, leave_room

from app.extensions import db, socketio
from app.models import ChatMessage, SessionAttendance


def register_socket_handlers(app):
    @socketio.on("connect")
    def handle_connect():
        emit("connected", {"message": "Connected to EventNet"})

    @socketio.on("authenticate")
    def handle_authenticate(data):
        try:
            token = data.get("token", "").replace("Bearer ", "")
            decoded = decode_token(token)
            user_id = decoded["sub"]
            join_room(f"user_{user_id}")
            emit("authenticated", {"user_id": user_id})
        except Exception:
            emit("error", {"message": "Authentication failed"})

    @socketio.on("join_event")
    def handle_join_event(data):
        event_id = data.get("event_id")
        session_id = data.get("session_id")
        user_id = data.get("user_id")
        if event_id:
            join_room(f"event_{event_id}")
            emit("user_joined", {"user_id": user_id, "event_id": event_id}, room=f"event_{event_id}")
        if session_id and user_id:
            join_room(f"session_{session_id}")
            attendance = SessionAttendance.query.filter_by(session_id=session_id, user_id=user_id).first()
            if not attendance:
                from datetime import datetime, timezone
                attendance = SessionAttendance(session_id=session_id, user_id=user_id, joined_at=datetime.now(timezone.utc))
                db.session.add(attendance)
                db.session.commit()

    @socketio.on("leave_event")
    def handle_leave_event(data):
        event_id = data.get("event_id")
        session_id = data.get("session_id")
        user_id = data.get("user_id")
        if event_id:
            leave_room(f"event_{event_id}")
            emit("user_left", {"user_id": user_id}, room=f"event_{event_id}")
        if session_id:
            leave_room(f"session_{session_id}")

    @socketio.on("session_chat")
    def handle_session_chat(data):
        message = ChatMessage(
            sender_id=data["sender_id"],
            receiver_id=0,
            session_id=data["session_id"],
            content=data["content"],
            message_type="session",
        )
        db.session.add(message)
        db.session.commit()
        emit("session_message", message.to_dict(), room=f"session_{data['session_id']}")

    @socketio.on("reaction")
    def handle_reaction(data):
        emit("reaction", data, room=f"session_{data.get('session_id')}")

    @socketio.on("announcement")
    def handle_announcement(data):
        emit("announcement", data, room=f"event_{data.get('event_id')}")


def emit_notification(user_id, notification):
    socketio.emit("notification", notification, room=f"user_{user_id}")


def emit_poll_update(event_id, session_id, poll_data):
    room = f"session_{session_id}" if session_id else f"event_{event_id}"
    socketio.emit("poll_update", poll_data, room=room)


def emit_new_question(event_id, session_id, question_data):
    socketio.emit("new_question", question_data, room=f"session_{session_id}")
