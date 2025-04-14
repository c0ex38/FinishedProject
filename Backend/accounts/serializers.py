from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password',
            'first_name', 'last_name',
            'bio', 'profile_picture',
            'gender',
            'latitude', 'longitude', 'location_name', 'is_location_visible',
            'phone_number', 'date_of_birth', 'website', 'is_private', 'signup_method'
        ]
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True, 'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'bio': {'required': True},
            'profile_picture': {'required': True},
            'gender': {'required': True},
            'latitude': {'required': True},
            'longitude': {'required': True},
            'location_name': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email adresi zaten kullanılıyor.")
        return value
