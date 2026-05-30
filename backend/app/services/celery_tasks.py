from app.extensions import celery_app


@celery_app.task(name="send_reminder_email")
def send_reminder_email(user_email, event_title, event_date):
    from app.notifications.service import NotificationService
    body = f"<p>Reminder: <strong>{event_title}</strong> is coming up on {event_date}.</p>"
    NotificationService.send_email(user_email, f"Event Reminder: {event_title}", body)


@celery_app.task(name="generate_analytics_report")
def generate_analytics_report(event_id):
    from app.services.analytics_service import AnalyticsService
    return AnalyticsService.event_analytics(event_id)
