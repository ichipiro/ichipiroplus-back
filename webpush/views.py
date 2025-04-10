import base64
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from pywebpush import webpush, WebPushException
import json
from django.conf import settings
import urllib
from .models import PushSubscription, PushNotificationLog
from .serializers import PushSubscriptionSerializer
import logging

logger = logging.getLogger(__name__)


class PushSubscriptionView(APIView):
    """プッシュ通知のサブスクリプションを管理するAPI"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ユーザーのサブスクリプション設定を取得"""
        subscriptions = PushSubscription.objects.filter(user=request.user)
        serializer = PushSubscriptionSerializer(subscriptions, many=True)

        return Response(serializer.data)

    def post(self, request):
        """プッシュ通知のサブスクリプションを登録する"""
        try:
            subscription_data = request.data

            # エンドポイントと鍵情報が含まれているか確認
            if not all(key in subscription_data for key in ["endpoint", "keys"]):
                return Response(
                    {"error": "Invalid subscription data"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # サブスクリプションを保存
            subscription, created = PushSubscription.objects.update_or_create(
                user=request.user,
                endpoint=subscription_data["endpoint"],
                defaults={
                    "p256dh": subscription_data["keys"]["p256dh"],
                    "auth": subscription_data["keys"]["auth"],
                    # オプションの通知設定
                    "task_reminders": subscription_data.get("task_reminders", True),
                    "new_articles": subscription_data.get("new_articles", True),
                    "system_notices": subscription_data.get("system_notices", True),
                },
            )

            return Response(
                {
                    "success": True,
                    "created": created,
                    "subscription": PushSubscriptionSerializer(subscription).data,
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"サブスクリプション登録エラー: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request):
        """プッシュ通知のサブスクリプションを削除する"""
        try:
            endpoint = request.data.get("endpoint")
            if not endpoint:
                return Response(
                    {"error": "Endpoint is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            deleted, _ = PushSubscription.objects.filter(
                user=request.user, endpoint=endpoint
            ).delete()

            return Response(
                {"success": True, "deleted": deleted > 0}, status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"サブスクリプション削除エラー: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateNotificationSettingsView(APIView):
    """通知設定を更新するAPI"""

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            endpoint = request.data.get("endpoint")
            if not endpoint:
                return Response(
                    {"error": "Endpoint is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            settings_data = {
                "task_reminders": request.data.get("task_reminders"),
                "new_articles": request.data.get("new_articles"),
                "system_notices": request.data.get("system_notices"),
            }

            # Noneの値はアップデートから除外
            settings_data = {k: v for k, v in settings_data.items() if v is not None}

            if not settings_data:
                return Response(
                    {"error": "No settings provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription = PushSubscription.objects.filter(
                user=request.user, endpoint=endpoint
            ).first()

            if not subscription:
                return Response(
                    {"error": "Subscription not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 設定を更新
            for key, value in settings_data.items():
                setattr(subscription, key, value)

            subscription.save()

            return Response(
                {
                    "success": True,
                    "subscription": PushSubscriptionSerializer(subscription).data,
                }
            )

        except Exception as e:
            logger.error(f"通知設定更新エラー: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def get_audience_from_endpoint(endpoint):
    parsed_url = urllib.parse.urlparse(endpoint)
    audience = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return audience


class TestPushNotificationView(APIView):
    """テスト通知を送信するAPI"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """テスト通知を送信する"""
        try:
            title = request.data.get("title", "テスト通知")
            body = request.data.get(
                "body", "これはバックエンドから送信されたテスト通知です"
            )
            url = request.data.get("url", "/notifications")

            result = send_push_notification(
                user=request.user,
                title=title,
                body=body,
                url=url,
                notification_type="test",
            )

            response_data = {
                "success": result["success"] > 0,
                "sent": result["success"],
                "errors": result["errors"] if result["errors"] else None,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"テスト通知エラー: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def send_push_notification(user, title, body, url=None, notification_type="general"):
    """
    特定のユーザーにプッシュ通知を送信するユーティリティ関数

    Args:
        user: 通知を送信するユーザー
        title: 通知のタイトル
        body: 通知の本文
        url: 通知クリック時のリダイレクト先URL（オプション）
        notification_type: 通知の種類 ('task', 'article', 'system'など)

    Returns:
        dict: 送信結果の情報
    """
    results = {"success": 0, "failed": 0, "errors": []}

    try:
        # ユーザーの通知設定に応じてフィルタリング
        subscriptions = PushSubscription.objects.filter(user=user)

        # 通知タイプに応じた設定をチェック
        if notification_type == "task":
            subscriptions = subscriptions.filter(task_reminders=True)
        elif notification_type == "article":
            subscriptions = subscriptions.filter(new_articles=True)
        elif notification_type == "system":
            subscriptions = subscriptions.filter(system_notices=True)

        if not subscriptions:
            results["errors"].append("No active subscriptions found")
            return results

        # 送信するデータ
        payload = json.dumps(
            {"title": title, "body": body, "url": url or "/", "type": notification_type}
        )

        # 各サブスクリプションに通知を送信
        for subscription in subscriptions:
            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
            }

            vapid_claims = {
                "sub": f"mailto:{settings.VAPID_CLAIMS_EMAIL}",
                "exp": int(time.time()) + 12 * 60 * 60,  # 有効期限を12時間に設定
                "aud": get_audience_from_endpoint(subscription.endpoint),
            }

            try:
                webpush(
                    subscription_info=subscription_info,
                    data=payload,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims=vapid_claims,
                    ttl=60 * 60 * 12,
                )
                results["success"] += 1

                # 通知ログを保存
                PushNotificationLog.objects.create(
                    user=user,
                    title=title,
                    body=body,
                    url=url,
                    notification_type=notification_type,
                    status="sent",
                )

            except WebPushException as e:
                logger.error(e)
                error_msg = str(e)
                results["failed"] += 1
                results["errors"].append(error_msg)

                # 無効なサブスクリプションの場合は削除
                if e.response and e.response.status_code in [404, 410]:
                    deleted = subscription.delete()
                    logger.info(f"Delete result: {deleted}")
                    results["errors"].append(
                        f"Invalid subscription removed: {subscription.endpoint}"
                    )

                logger.error(f"通知送信エラー (User: {user.username}): {error_msg}")

                # エラーログを保存
                PushNotificationLog.objects.create(
                    user=user,
                    title=title,
                    body=body,
                    url=url,
                    notification_type=notification_type,
                    status="failed",
                )

    except Exception as e:
        error_msg = str(e)
        results["errors"].append(error_msg)
        logger.error(f"通知送信処理エラー: {error_msg}")

    return results
