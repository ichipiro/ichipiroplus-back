import logging
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from accounts.models import UserProfile
from .models import Article
from .serializers import ArticleSerializer
from django.db import models

logger = logging.getLogger(__name__)


class ArticlePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "size"
    max_page_size = 100


class AuthorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # 全ての操作に認証が必要
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # 記事の読み取りは queryset でフィルタリング済みのため常に許可
        if request.method in permissions.SAFE_METHODS:
            return True

        # 変更・削除は著者のみ許可
        return obj.author == request.user


class UploadImageView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")  # Tiptap側が"file"キーを送る想定
        if not file_obj:
            return Response({"error": "No file uploaded."}, status=400)

        ext = file_obj.name.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        try:
            saved_path = default_storage.save(f"articles/{filename}", file_obj)
        except Exception as e:
            logger.error(e.args)

        url = default_storage.url(saved_path)

        return Response({"url": url}, status=200)


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [AuthorPermission]
    pagination_class = ArticlePagination
    lookup_field = "id"  # slugからidに変更

    def get_queryset(self):
        return Article.objects.filter(
            models.Q(is_public=True) | models.Q(author=self.request.user)
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserArticleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [AuthorPermission]
    pagination_class = ArticlePagination
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        profile_id = self.kwargs.get("profile_id")
        try:
            profile = UserProfile.objects.get(profile_id=profile_id)
            user = profile.user

            # 基本のクエリセット 特定ユーザーの記事のみ
            queryset = Article.objects.filter(author=user)

            # 著者以外のユーザーには公開記事のみ表示
            if self.request.user != user:
                queryset = queryset.filter(is_public=True)

            return queryset.order_by("-created_at")

        except UserProfile.DoesNotExist:
            return Article.objects.none()
