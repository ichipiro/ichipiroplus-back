from django.urls import path
from .views import (
    DepartmentListView,
    FacultyListView,
    ProfileDetailView,
    ProfileView,
    UploadImageView,
)

urlpatterns = [
    path("me/profile/", ProfileView.as_view(), name="profile-detail"),
    path(
        "profiles/<str:profile_id>/", ProfileDetailView.as_view(), name="profile-by-id"
    ),
    path("faculties/", FacultyListView.as_view(), name="faculty-list"),
    path("departments/", DepartmentListView.as_view(), name="department-list"),
    path("upload/", UploadImageView.as_view(), name="upload-image"),
]
