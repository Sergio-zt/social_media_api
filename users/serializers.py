from rest_framework import serializers
from django.contrib.auth import get_user_model

# Using get_user_model() is the recommended way to reference the custom User model
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles the creation of a new user and safely hashes the password.
    """
    # Explicitly define password field to ensure it's write-only
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'password')

    def create(self, validated_data):
        # We must use create_user method from our UserManager 
        # so the password gets hashed correctly.
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating user profile information.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'bio', 'avatar', 'date_joined')
        # 'email' and 'date_joined' shouldn't be editable through the profile update endpoint
        read_only_fields = ('id', 'email', 'date_joined')