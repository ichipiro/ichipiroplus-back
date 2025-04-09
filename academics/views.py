from django.shortcuts import get_object_or_404
from rest_framework import generics
import logging
from academics.filters import RegistrationFilter, LectureFilter
from .utils import get_current_term_and_year
from .models import Lecture, Registration, Schedule
from rest_framework import viewsets, permissions
from .serializers import (
    LectureSerializer,
    RegistrationSerializer,
    ScheduleSerializer,
)
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class IsOwnerOrPublicEditable(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 所有者は常に編集可能
        if obj.owner == request.user:
            return True

        # 公開編集可能フラグがTrueの場合は認証ユーザーが編集可能
        if obj.is_public_editable:
            return True

        return False


class LectureViewSet(viewsets.ModelViewSet):
    serializer_class = LectureSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LectureFilter

    def get_queryset(self):
        user = self.request.user

        # 基本クエリ: 自分が所有者か、公開されている講義
        base_query = Q(owner=user) | Q(is_public=True)

        # ユーザーの所属学科に関連する講義
        dept_faculty_query = (
            Q(syllabus__isnull=False)
            & Q(syllabus__departments=user.profile.department)
            & Q(syllabus__departments__faculty=user.profile.faculty)
        ) | Q(
            syllabus__isnull=True
        )  # シラバスがない講義はすべて表示

        return Lecture.objects.filter(base_query & dept_faculty_query).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrPublicEditable]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RegistrationFilter

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ScheduleListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class CurrentTermView(APIView):
    def get(self, request, *args, **kwargs):
        current_term, fiscal_year = get_current_term_and_year()

        if not current_term:
            return Response(
                {"error": "現在のタームが見つかりません。"},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_data = {
            "year": fiscal_year,
            "term": {
                "number": current_term.number,
                "name": str(current_term),
                "start_date": current_term.start_date.isoformat(),
                "end_date": current_term.end_date.isoformat(),
            },
        }

        return Response(response_data)


class AttendanceView(APIView):
    """
    出席回数を管理するAPI
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, registration_id):
        """
        出席回数をインクリメントする
        """
        # 自分の登録情報のみ更新可能
        registration = get_object_or_404(
            Registration, id=registration_id, user=request.user
        )

        # 出席回数をインクリメント
        registration.increment_attendance()

        serializer = RegistrationSerializer(registration)
        return Response(serializer.data)

    def delete(self, request, registration_id):
        """
        出席回数をデクリメントする
        """
        # 自分の登録情報のみ更新可能
        registration = get_object_or_404(
            Registration, id=registration_id, user=request.user
        )

        # 出席回数をデクリメント
        registration.decrement_attendance()

        serializer = RegistrationSerializer(registration)
        return Response(serializer.data)
