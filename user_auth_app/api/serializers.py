import os

from django.contrib.auth.models import User
from rest_framework import serializers

from user_auth_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Basic serializer for reading and writing UserProfile data.
    """
    class Meta:
        model = UserProfile
        fields = '__all__'


class RegistrationSerializer(serializers.Serializer):
    """
    Handles user registration, including:
    - username, password, and repeated password
    - email
    - user type (e.g., customer or business)
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    type = serializers.ChoiceField(choices=UserProfile.USERTYPE_CHOICES)

    def validate_username(self, value):
        """
        Check if the username already exists.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username already exists.')
        return value

    def validate_email(self, value):
        """
        Check if the email is already used by another user.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email already exists.')
        return value
    
    def validate(self, obj):
        """
        Check if the two passwords match.
        """
        if obj['password'] != obj['repeated_password']:
            raise serializers.ValidationError('Passwords do not match.')
        return obj
    
    def create(self, validated_data):
        """
        Create a new user and a linked user profile.
        """
        validated_data.pop('repeated_password')
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        type = validated_data.pop('type')

        user = User.objects.create_user(username=username, email=email, password=password)
        userProfile = UserProfile.objects.create(user=user, type=type)
        return userProfile
