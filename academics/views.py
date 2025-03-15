from django.utils import timezone
from rest_framework import generics
import logging
from academics.filters import RegistrationFilter, LectureFilter
from .models import Lecture, Registration, Schedule, Term
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
        dept_faculty_query = Q(departments=user.profile.department) & Q(
            departments__faculty=user.profile.faculty
        )

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
        today = timezone.now().date()

        # 終了日が未来のタームを取得し、終了日が最も近いものを選択
        current_term = (
            Term.objects.filter(end_date__gte=today).order_by("end_date").first()
        )

        # 該当するタームがない場合、エラーを返す
        if not current_term:
            return Response(
                {"error": "現在のタームが見つかりません。"},
                status=status.HTTP_404_NOT_FOUND,
            )

        end_date = current_term.end_date
        fiscal_year = end_date.year

        # 1月〜3月の場合は前年度として扱う
        if end_date.month <= 3:
            fiscal_year -= 1

        response_data = {
            "year": fiscal_year,
            "term": {
                "number": current_term.number,
                "name": str(current_term),
                "end_date": current_term.end_date.isoformat(),
            },
        }

        return Response(response_data)
