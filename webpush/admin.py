from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages

from .models import PushSubscription, PushNotificationLog
from .views import send_push_notification
from django.contrib.auth.models import User


class PushNotificationForm(forms.Form):
    """プッシュ通知の送信フォーム"""

    title = forms.CharField(
        label="タイトル",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    body = forms.CharField(
        label="本文",
        required=True,
        widget=forms.Textarea(attrs={"class": "vLargeTextField"}),
    )
    url = forms.CharField(
        label="リンク先URL",
        max_length=500,
        required=False,
        initial="/",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    notification_type = forms.ChoiceField(
        label="通知タイプ",
        choices=[
            ("system", "システム通知"),
            ("task", "タスク通知"),
            ("article", "記事通知"),
        ],
        initial="system",
        widget=forms.RadioSelect,
    )
    recipient_type = forms.ChoiceField(
        label="送信先",
        choices=[
            ("all", "全ユーザー"),
            ("selected", "選択したユーザー"),
        ],
        initial="selected",
        widget=forms.RadioSelect,
    )
    users = forms.ModelMultipleChoiceField(
        label="ユーザー",
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "vSelectMultiple"}),
    )


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    """プッシュ通知サブスクリプションの管理画面"""

    list_display = (
        "user",
        "endpoint_short",
        "task_reminders",
        "new_articles",
        "system_notices",
        "created_at",
    )
    list_filter = ("task_reminders", "new_articles", "system_notices", "created_at")
    search_fields = ("user__username", "user__email", "endpoint")
    date_hierarchy = "created_at"

    def endpoint_short(self, obj):
        """エンドポイントを短く表示"""
        if len(obj.endpoint) > 50:
            return f"{obj.endpoint[:50]}..."
        return obj.endpoint

    endpoint_short.short_description = "エンドポイント"


@admin.register(PushNotificationLog)
class PushNotificationLogAdmin(admin.ModelAdmin):
    """プッシュ通知ログの管理画面"""

    list_display = ("title", "user", "notification_type", "status", "sent_at")
    list_filter = ("notification_type", "status", "sent_at")
    search_fields = ("title", "body", "user__username", "user__email")
    date_hierarchy = "sent_at"
    readonly_fields = (
        "title",
        "body",
        "url",
        "user",
        "notification_type",
        "status",
        "sent_at",
    )

    def has_add_permission(self, request):
        """追加権限を無効化"""
        return False

    def has_change_permission(self, request, obj=None):
        """変更権限を無効化"""
        return False

    # 通知送信機能を追加
    def get_urls(self):
        """URLの追加"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "send-notification/",
                self.admin_site.admin_view(self.send_notification_view),
                name="send-notification",
            ),
        ]
        return custom_urls + urls

    def send_notification_view(self, request):
        """通知送信ビュー"""
        if request.method == "POST":
            form = PushNotificationForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data["title"]
                body = form.cleaned_data["body"]
                url = form.cleaned_data["url"]
                notification_type = form.cleaned_data["notification_type"]
                recipient_type = form.cleaned_data["recipient_type"]
                selected_users = form.cleaned_data["users"]

                success_count = 0
                failure_count = 0

                if recipient_type == "all":
                    # 全ユーザーに送信
                    users = User.objects.all()
                else:
                    # 選択したユーザーに送信
                    users = selected_users

                for user in users:
                    result = send_push_notification(
                        user=user,
                        title=title,
                        body=body,
                        url=url,
                        notification_type=notification_type,
                    )
                    success_count += result["success"]
                    failure_count += result["failed"]

                self.message_user(
                    request,
                    f"通知を送信しました。成功: {success_count}, 失敗: {failure_count}",
                    level=messages.SUCCESS if success_count > 0 else messages.WARNING,
                )
                return redirect("admin:webpush_pushnotificationlog_changelist")
        else:
            form = PushNotificationForm()

        context = {
            "form": form,
            "title": "通知の送信",
            "opts": self.model._meta,
            "has_change_permission": self.has_change_permission(request),
        }
        return render(request, "admin/webpush/send_notification.html", context)

    def changelist_view(self, request, extra_context=None):
        """一覧画面に通知送信ボタンを追加"""
        extra_context = extra_context or {}
        extra_context["show_send_notification_button"] = True
        return super().changelist_view(request, extra_context=extra_context)
