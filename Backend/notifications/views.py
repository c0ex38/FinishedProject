from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """
    Get user's notifications
    """
    notifications = request.user.notifications.all()
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notifications_read(request):
    """
    Mark all unread notifications as read
    """
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    return Response({'status': 'notifications marked as read'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_notifications(request):
    """
    Delete all notifications
    """
    request.user.notifications.all().delete()
    return Response({'status': 'notifications cleared'})
