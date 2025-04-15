from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Group, GroupMember, GroupPost, GroupPostComment,
    GroupChat, GroupChatMessage, GroupEvent, GroupEventParticipant
)

User = get_user_model()

class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']

class GroupSerializer(serializers.ModelSerializer):
    creator = UserBriefSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    user_membership = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'slug', 'description', 'group_type', 
                 'creator', 'cover_image', 'created_at', 'member_count',
                 'user_membership']
        read_only_fields = ['creator', 'created_at']
    
    def get_member_count(self, obj):
        return obj.members.filter(status='approved').count()
    
    def get_user_membership(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = obj.members.filter(user=request.user).first()
            if membership:
                return {
                    'role': membership.role,
                    'status': membership.status
                }
        return None

class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    
    class Meta:
        model = GroupMember
        fields = ['id', 'user', 'role', 'status', 'joined_at']
        read_only_fields = ['joined_at']

class GroupPostCommentSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    
    class Meta:
        model = GroupPostComment
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['author', 'created_at']

class GroupPostSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    comments = GroupPostCommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupPost
        fields = ['id', 'author', 'content', 'image', 'created_at',
                 'comments', 'comment_count']
        read_only_fields = ['author', 'created_at']
    
    def get_comment_count(self, obj):
        return obj.comments.count()

class GroupChatMessageSerializer(serializers.ModelSerializer):
    sender = UserBriefSerializer(read_only=True)

    class Meta:
        model = GroupChatMessage
        fields = ['id', 'sender', 'content', 'image', 'created_at']
        read_only_fields = ['sender', 'created_at']

class GroupChatSerializer(serializers.ModelSerializer):
    messages = GroupChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = GroupChat
        fields = ['id', 'messages', 'created_at']
        read_only_fields = ['created_at']