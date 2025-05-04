from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "user_type",
            "is_active",
            "is_staff",
            "organisation_name",
            "first_name",
            "last_name",
            "logo",
        ]
