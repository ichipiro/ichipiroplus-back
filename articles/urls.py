from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, UploadImageView, UserArticleViewSet

router = DefaultRouter()
router.register(r"list", ArticleViewSet, basename="article")

user_router = DefaultRouter()
user_router.register(r"", UserArticleViewSet, basename="user-article")

urlpatterns = [
    path("", include(router.urls)),
    path("upload/", UploadImageView.as_view(), name="upload_image"),
    path("by-user/<str:profile_id>/", include(user_router.urls)),
]
