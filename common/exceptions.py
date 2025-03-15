from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
import logging

logger = logging.getLogger("django.request")


def custom_exception_handler(exc, context):
    # まずDRFの標準ハンドラを呼び出す
    response = exception_handler(exc, context)

    # リクエスト情報を取得
    request = context.get("request")
    view = context.get("view")
    view_name = view.__class__.__name__ if view else "Unknown"

    # エラーコードとデフォルトメッセージの設定
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = str(exc)
    code = "server_error"

    if response is not None:
        # DRFが認識した例外の場合
        status_code = response.status_code
        data = response.data

        # レスポンスデータの形式によって処理を分ける
        if isinstance(data, dict):
            detail = data.get("detail", str(data))
        elif isinstance(data, list):
            detail = data[0] if data else "Multiple errors occurred"
        else:
            detail = str(data)

        # HTTPステータスコードに基づいてエラーコードを設定
        if status_code == 400:
            code = "invalid_request"
        elif status_code == 401:
            code = "authentication_failed"
        elif status_code == 403:
            code = "permission_denied"
        elif status_code == 404:
            code = "not_found"
        elif status_code == 405:
            code = "method_not_allowed"
        elif status_code == 429:
            code = "throttled"
    else:
        # DRFが認識しない例外
        response = Response(status=status_code)

    # エラーログ出力
    log_level = logging.ERROR if status_code >= 500 else logging.WARNING
    logger.log(
        log_level,
        f"{code}: {detail}",
        extra={
            "status_code": status_code,
            "view": view_name,
            "path": request.path if request else "Unknown",
            "method": request.method if request else "Unknown",
            "user_id": (
                request.user.id
                if request
                and hasattr(request, "user")
                and request.user.is_authenticated
                else None
            ),
        },
    )

    # エラーレスポンスの統一フォーマット
    response.data = {
        "error": {
            "code": code,
            "message": detail,
            "status": status_code,
        }
    }

    return response


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "サービスは現在利用できません。"
    default_code = "service_unavailable"


class ValidationError(APIException):
    status_code = 400
    default_detail = "データ検証エラー"
    default_code = "validation_error"


class ResourceConflict(APIException):
    status_code = 409
    default_detail = "リソースの競合が発生しました。"
    default_code = "resource_conflict"


class BusinessLogicError(APIException):
    status_code = 400
    default_detail = "ビジネスルールに違反しています。"
    default_code = "business_rule_violation"
