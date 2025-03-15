from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LectureViewSet,
    RegistrationViewSet,
    ScheduleListView,
    CurrentTermView,
)

router = DefaultRouter()
router.register(r"lectures", LectureViewSet, basename="lecture")
router.register(r"registrations", RegistrationViewSet, basename="registration")

urlpatterns = [
    path("schedules/", ScheduleListView.as_view(), name="schedule"),
    path("now/", CurrentTermView.as_view(), name="now"),
    path("", include(router.urls)),
]
