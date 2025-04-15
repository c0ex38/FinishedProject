from rest_framework import serializers
from .models import Event, EventParticipant, EventComment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']

class EventCommentSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    
    class Meta:
        model = EventComment
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']

class EventParticipantSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    
    class Meta:
        model = EventParticipant
        fields = ['id', 'user', 'status', 'created_at']
        read_only_fields = ['user', 'created_at']

class EventSerializer(serializers.ModelSerializer):
    organizer = UserBriefSerializer(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    user_participation = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'organizer', 'title', 'description', 'event_type',
            'start_date', 'end_date', 'location', 'online_link',
            'max_participants', 'cover_image', 'is_public',
            'participant_count', 'is_past', 'is_ongoing',
            'user_participation', 'created_at'
        ]
        read_only_fields = ['organizer', 'created_at']
    
    def get_user_participation(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            participation = obj.participants.filter(user=request.user).first()
            if participation:
                return EventParticipantSerializer(participation).data
        return None