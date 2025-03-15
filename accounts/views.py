import uuid
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from allauth.socialaccount.providers.microsoft.views import MicrosoftGraphOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from .models import Department, Faculty, UserProfile
from rest_framework.response import Response
from .serializers import (
    DepartmentSerializer,
    FacultySerializer,
    UserProfileSerializer,
    UserWithProfileSerializer,
)
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework import status


class FacultyListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer


class DepartmentListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UploadImageView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")  # Tiptap側が"file"キーを送る想定
        if not file_obj:
            return Response({"error": "No file uploaded."}, status=400)

        ext = file_obj.name.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        saved_path = default_storage.save(f"profile/{filename}", file_obj)
        url = default_storage.url(saved_path)

        return Response({"url": url}, status=200)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 更新後のプロフィール完了状態をレスポンスに含める
        result = serializer.data
        return Response(result)


class ProfileDetailView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]
    lookup_field = "profile_id"
    lookup_url_kwarg = "profile_id"

    def get_queryset(self):
        return UserProfile.objects.all()


class MicrosoftLogin(SocialLoginView):
    adapter_class = MicrosoftGraphOAuth2Adapter
    callback_url = "http://localhost:3000/api/auth/callback/microsoft-entra-id"
    client_class = OAuth2Client

    def get_response(self):
        # オリジナルのレスポンスを取得（トークン情報など）
        original_response = super().get_response()
        original_data = original_response.data

        # ユーザー情報をUserWithProfileSerializerでシリアライズ
        user_data = UserWithProfileSerializer(self.user).data

        # 両方のデータを結合
        response_data = {**original_data, "user": user_data}

        return Response(response_data)
