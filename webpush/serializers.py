from rest_framework import serializers
from .models import PushSubscription, PushNotificationLog


class PushSubscriptionSerializer(serializers.ModelSerializer):
    """プッシュ通知サブスクリプションのシリアライザ"""

    class Meta:
        model = PushSubscription
        fields = [
            "id",
            "endpoint",
            "task_reminders",
            "new_articles",
            "system_notices",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PushNotificationLogSerializer(serializers.ModelSerializer):
    """プッシュ通知ログのシリアライザ"""

    class Meta:
        model = PushNotificationLog
        fields = [
            "id",
            "title",
            "body",
            "url",
            "notification_type",
            "sent_at",
            "status",
        ]
        read_only_fields = ["id", "sent_at"]
