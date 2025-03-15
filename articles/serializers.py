from rest_framework import serializers
from accounts.serializers import UserWithProfileSerializer
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    author = UserWithProfileSerializer(read_only=True)

    class Meta:
        model = Article
        fields = (
            "id",
            "slug",
            "title",
            "content_json",
            "content_html",
            "author",
            "is_public",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "author", "created_at", "updated_at")
