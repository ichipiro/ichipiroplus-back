from django.urls import path, include

urlpatterns = [
    path(
        "v1/",
        include(
            [
                # 認証関連
                path("auth/", include("accounts.auth_urls")),
                # ユーザー関連
                path("users/", include("accounts.user_urls")),
                # 学術情報関連（アカデミック情報）
                path("academics/", include("academics.urls")),
                # タスク関連
                path("tasks/", include("tasks.urls")),
                # 記事関連
                path("articles/", include("articles.urls")),
                path("push/", include("webpush.urls")),
            ]
        ),
    ),
]
