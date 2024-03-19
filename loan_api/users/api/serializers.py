from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    model = User
    fields = (
        "id",
        "email",
        "username",
        "password",
        "first_name",
        "last_name",
        "is_admin",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    read_only_fields = ["id", "is_staff", "is_superuser"]
    extra_kwargs = {"password": {"write_only": True}}
