from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "プロフィール情報"
    fk_name = "user"


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "get_display_name",
        "get_faculty",
        "get_department",
        "is_staff",
    )
    search_fields = ("username", "email", "profile__user_id", "profile__display_name")

    def get_display_name(self, obj):
        return obj.profile.display_name if hasattr(obj, "profile") else ""

    get_display_name.short_description = "表示名"

    def get_faculty(self, obj):
        if hasattr(obj, "profile") and obj.profile.faculty:
            return obj.profile.faculty.name
        return ""

    get_faculty.short_description = "学部"

    def get_department(self, obj):
        if hasattr(obj, "profile") and obj.profile.department:
            return obj.profile.department.name
        return ""

    get_department.short_description = "学科"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
