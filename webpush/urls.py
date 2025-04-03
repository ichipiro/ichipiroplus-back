from django.urls import path
from .views import (
    PushSubscriptionView,
    TestPushNotificationView,
    UpdateNotificationSettingsView,
)

urlpatterns = [
    path(
        "register/", PushSubscriptionView.as_view(), name="push_subscription_register"
    ),
    path(
        "unregister/",
        PushSubscriptionView.as_view(),
        name="push_subscription_unregister",
    ),
    path(
        "settings/",
        UpdateNotificationSettingsView.as_view(),
        name="push_notification_settings",
    ),
    path("test/", TestPushNotificationView.as_view(), name="push_notification_test"),
]
