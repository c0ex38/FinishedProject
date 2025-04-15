from rest_framework import serializers
from .models import Hashtag, PostHashtag
from posts.serializers import PostSerializer

class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'slug', 'post_count', 'created_at']
        read_only_fields = ['slug', 'post_count', 'created_at']

class PostHashtagSerializer(serializers.ModelSerializer):
    hashtag = HashtagSerializer(read_only=True)
    
    class Meta:
        model = PostHashtag
        fields = ['id', 'hashtag', 'created_at']
        read_only_fields = ['created_at']