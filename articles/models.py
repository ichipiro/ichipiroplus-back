import uuid
import shortuuid
from django.db import models
from django.contrib.auth.models import User


def generate_short_uuid():
    return shortuuid.ShortUUID().random(length=16)


class Article(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    slug = models.CharField(
        default=generate_short_uuid,
        max_length=32,
    )
    author = models.ForeignKey(
        User,
        related_name="articles",
        on_delete=models.CASCADE,
        verbose_name="著者",
    )
    title = models.CharField(max_length=64)
    content_json = models.JSONField()  # TiptapエディタのJSON本文を格納
    content_html = models.TextField(null=True)
    is_public = models.BooleanField(default=False)  # 公開
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "記事"
        unique_together = ['author', 'slug']  # 著者ごとにslugをユニークに

    def __str__(self):
        return self.title
