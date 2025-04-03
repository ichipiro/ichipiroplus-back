from django.db import models
from django.contrib.auth.models import User


class PushSubscription(models.Model):
    """プッシュ通知のサブスクリプション情報を保存するモデル"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="push_subscriptions"
    )
    endpoint = models.TextField()
    p256dh = models.TextField()
    auth = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 設定フラグ
    task_reminders = models.BooleanField(default=True)
    new_articles = models.BooleanField(default=True)
    system_notices = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "endpoint")
        verbose_name = "プッシュ通知サブスクリプション"
        verbose_name_plural = "プッシュ通知サブスクリプション"

    def __str__(self):
        return f"{self.user.username}のプッシュ通知設定"


class PushNotificationLog(models.Model):
    """送信されたプッシュ通知の履歴を記録するモデル"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="push_logs")
    title = models.CharField(max_length=255)
    body = models.TextField()
    url = models.CharField(max_length=500, blank=True, null=True)
    notification_type = models.CharField(
        max_length=50
    )  # 'task', 'article', 'system' など
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="sent")  # 'sent', 'failed' など

    class Meta:
        verbose_name = "プッシュ通知ログ"
        verbose_name_plural = "プッシュ通知ログ"
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.title} ({self.sent_at.strftime('%Y-%m-%d %H:%M')})"
