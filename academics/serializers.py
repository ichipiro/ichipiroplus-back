from rest_framework import serializers

from academics.constants import TERM_CHOICES
from accounts.models import Department
from accounts.serializers import DepartmentSerializer, UserWithProfileSerializer
from common.exceptions import ValidationError

from .models import Lecture, Registration, Schedule, Syllabus, Term


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ["number", "end_date"]

    def validate_number(self, value):
        if value not in dict(TERM_CHOICES):
            raise serializers.ValidationError(
                "タームは1から4の間でなければなりません。"
            )
        return value


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["id", "day", "time"]


class SyllabusSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True, read_only=True)
    schedule_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Schedule.objects.all(), write_only=True, source="schedules"
    )

    departments = DepartmentSerializer(many=True, read_only=True)
    department_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Department.objects.all(),
        write_only=True,
        source="departments",
    )

    class Meta:
        model = Syllabus
        fields = [
            "id",
            "name",
            "units",
            "schedules",
            "schedule_ids",
            "departments",
            "department_ids",
            "instructor",
            "grade",
            "purpose",
            "goal",
            "is_required",
            "is_exam",
            "description",
            "eval_method",
            "textbook",
            "feedback",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]


class LectureSerializer(serializers.ModelSerializer):
    terms = TermSerializer(many=True, read_only=True)

    schedules = ScheduleSerializer(many=True, read_only=True)
    term_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Term.objects.all(), write_only=True, source="terms"
    )
    schedule_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Schedule.objects.all(), write_only=True, source="schedules"
    )
    # シラバスから必要な情報のみを取得
    departments = DepartmentSerializer(
        source="syllabus.departments", many=True, read_only=True
    )
    is_required = serializers.BooleanField(
        source="syllabus.is_required", read_only=True, allow_null=True
    )
    is_exam = serializers.BooleanField(
        source="syllabus.is_exam", read_only=True, allow_null=True
    )

    owner = UserWithProfileSerializer(read_only=True)

    class Meta:
        model = Lecture
        fields = [
            "id",
            "syllabus",
            "name",
            "terms",
            "schedules",
            "term_ids",
            "schedule_ids",
            "grade",
            "room",
            "instructor",
            "is_required",
            "is_exam",
            "biko",
            "departments",
            "is_public",
            "is_public_editable",
            "owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "owner",
            "is_public",
            "is_public_editable",
        ]

    def to_representation(self, instance):
        """
        シリアライズ時にシラバスが存在しない場合のハンドリング
        """
        data = super().to_representation(instance)
        if not instance.syllabus:
            data["is_required"] = None
            data["is_exam"] = None
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    lecture = LectureSerializer(read_only=True)
    lecture_id = serializers.PrimaryKeyRelatedField(
        queryset=Lecture.objects.all(),
        write_only=True,
        source="lecture",
    )

    class Meta:
        model = Registration
        fields = ["id", "lecture", "lecture_id", "year", "registered_at"]
        read_only_fields = ["registered_at"]

    def validate(self, data):
        user = self.context["request"].user
        lecture = data.get("lecture")
        year = data.get("year")

        if not user.is_authenticated:
            raise ValidationError("認証が必要です。")

        # 取得する講義のタームとスケジュール
        new_lecture_terms = lecture.terms.all()
        new_lecture_schedules = lecture.schedules.all()

        # 同じ年に既に登録している講義のタームとスケジュールを取得
        overlapping_registrations = Registration.objects.filter(
            user=user,
            year=year,
            lecture__terms__in=new_lecture_terms,
            lecture__schedules__in=new_lecture_schedules,
        ).distinct()

        if overlapping_registrations.exists():
            # 重複している講義の詳細を取得
            overlapping_lectures = overlapping_registrations.values_list(
                "lecture__name", flat=True
            )
            overlapping_lectures_str = ", ".join(overlapping_lectures)
            raise ValidationError(
                f"登録しようとしている講義の日程が（{overlapping_lectures_str}）と重複しています。"
            )

        return data
