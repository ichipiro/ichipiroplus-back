from django.db import models
from django.dispatch import receiver
import shortuuid
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from accounts.constants import GRADE_CHOICES


class Faculty(models.Model):
    name = models.CharField(max_length=30)  # 学部名

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=30)  # 学科名
    faculty = models.ForeignKey(
        Faculty, related_name="departments", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.name}"


def generate_short_uuid():
    return shortuuid.ShortUUID().random(length=16)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_id = models.CharField(
        unique=True, max_length=16, default=generate_short_uuid
    )
    introduction = models.TextField(max_length=300, null=True, blank=True)
    display_name = models.CharField(max_length=16)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.SET_NULL, null=True, blank=True
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    grade = models.PositiveSmallIntegerField(
        choices=GRADE_CHOICES, null=True, blank=True
    )
    picture = models.URLField(null=True, blank=True)
    is_profile_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.profile_id}のプロフィール"

    def check_profile_complete(self):
        # 必須フィールドをチェック
        if self.profile_id and self.display_name is not None:
            self.is_profile_complete = True
        else:
            self.is_profile_complete = False
        return self.is_profile_complete

    # ユーザーから簡単にデータを取得できるようにプロパティを追加
    @property
    def email(self):
        return self.user.email

    @property
    def username(self):
        return self.user.username

    @property
    def full_name(self):
        return (
            f"{self.user.first_name} {self.user.last_name}".strip() or self.display_name
        )


# ユーザー作成時に自動的にプロフィールを作成するシグナル
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
