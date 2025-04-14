from rest_framework import serializers
from .models import Post, PostMedia, Like, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']


class CommentSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'updated_at', 'parent', 'replies', 'reply_count']
        read_only_fields = ['user', 'created_at', 'updated_at', 'replies', 'reply_count']
    
    def get_replies(self, obj):
        # Only return direct replies if this is a parent comment
        if obj.parent is None:
            # Limit to first 3 replies
            replies = obj.replies.all()[:3]
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def get_reply_count(self, obj):
        if obj.parent is None:
            return obj.replies.count()
        return 0


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'media_type', 'order', 'created_at']
        read_only_fields = ['created_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    media = PostMediaSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    main_media = PostMediaSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'content', 
            'latitude', 'longitude', 'location_name',
            'created_at', 'updated_at', 'is_public',
            'likes_count', 'comments_count', 'shares_count',
            'media', 'main_media', 'comments', 'is_liked'
        ]
        read_only_fields = ['author', 'likes_count', 'comments_count', 'shares_count']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False