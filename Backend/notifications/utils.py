from .models import Notification

def create_notification(recipient, sender, notification_type, text, **kwargs):
    """
    Create a new notification
    """
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        text=text,
        **kwargs
    )
    return notification