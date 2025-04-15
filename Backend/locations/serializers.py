from rest_framework import serializers
from .models import Location, PostLocation
from posts.serializers import PostSerializer

class LocationSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True, required=False)
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude', 'address', 
                 'city', 'country', 'post_count', 'distance']

class PostLocationSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    post = PostSerializer()
    
    class Meta:
        model = PostLocation
        fields = ['id', 'post', 'location', 'created_at']