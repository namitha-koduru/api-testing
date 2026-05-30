from app.extensions import db
from app.models import Notification, NotificationType


class NotificationService:
    @staticmethod
    def create(user_id: int, type: NotificationType, title: str, message: str, link: str = None, metadata: dict = None):
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            link=link,
            metadata_json=metadata or {},
        )
        db.session.add(notification)
        db.session.commit()

        from app.websocket.handlers import emit_notification
        emit_notification(user_id, notification.to_dict())
        return notification

    @staticmethod
    def send_email(to: str, subject: str, body: str):
        sendgrid_key = current_app.config.get("SENDGRID_API_KEY")
        if sendgrid_key:
            try:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail

                message = Mail(
                    from_email=current_app.config["MAIL_DEFAULT_SENDER"],
                    to_emails=to,
                    subject=subject,
                    html_content=body,
                )
                SendGridAPIClient(sendgrid_key).send(message)
                return True
            except Exception:
                pass

        try:
            import smtplib
            from email.mime.text import MIMEText

            msg = MIMEText(body, "html")
            msg["Subject"] = subject
            msg["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
            msg["To"] = to

            with smtplib.SMTP(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"]) as server:
                if current_app.config["MAIL_USE_TLS"]:
                    server.starttls()
                if current_app.config["MAIL_USERNAME"]:
                    server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
                server.send_message(msg)
            return True
        except Exception:
            return False

    @staticmethod
    def mark_read(notification_id: int, user_id: int):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
        return notification

    @staticmethod
    def get_user_notifications(user_id: int, unread_only=False):
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return [n.to_dict() for n in query.order_by(Notification.created_at.desc()).limit(50).all()]
