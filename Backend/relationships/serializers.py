from rest_framework import serializers
from .models import UserRelationship
from django.contrib.auth import get_user_model

User = get_user_model()

class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']

class UserRelationshipSerializer(serializers.ModelSerializer):
    follower = UserBriefSerializer(read_only=True)
    followed = UserBriefSerializer(read_only=True)
    
    class Meta:
        model = UserRelationship
        fields = ['id', 'follower', 'followed', 'created_at']
        read_only_fields = ['follower', 'created_at']