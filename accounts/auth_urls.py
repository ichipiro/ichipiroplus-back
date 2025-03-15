from django.urls import include, path
from .views import (
    DeleteAccountView,
    MicrosoftLogin,
)

urlpatterns = [
    path("microsoft/", MicrosoftLogin.as_view(), name="microsoft_login"),
    path("allauth/", include("allauth.urls")),
    path("dj-rest-auth/", include("dj_rest_auth.urls")),
    path("registration/", include("dj_rest_auth.registration.urls")),
    path("delete-account/", DeleteAccountView.as_view(), name="delete_account"),
]
