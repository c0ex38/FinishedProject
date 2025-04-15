from rest_framework import serializers
from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserBriefSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'notification_type', 'text', 'is_read', 'created_at']
        read_only_fields = ['sender', 'notification_type', 'text', 'created_at']