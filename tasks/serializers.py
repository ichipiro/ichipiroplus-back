from rest_framework import serializers

from academics.models import Registration
from academics.serializers import RegistrationSerializer
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    registration = RegistrationSerializer(read_only=True)
    registration_id = serializers.PrimaryKeyRelatedField(
        queryset=Registration.objects.all(),
        write_only=True,
        source="registration",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "registration",
            "registration_id",
            "title",
            "description",
            "status",
            "due_date",
            "priority",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )
