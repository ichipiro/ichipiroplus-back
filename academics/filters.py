import django_filters

from accounts.models import Department
from .models import Lecture, Registration, Schedule, Term


class LectureFilter(django_filters.FilterSet):
    terms = django_filters.ModelMultipleChoiceFilter(
        field_name="terms",
        queryset=Term.objects.all(),
        label="ターム",
    )
    department = django_filters.NumberFilter(
        field_name="syllabus__departments", lookup_expr="exact"
    )
    departments = django_filters.ModelMultipleChoiceFilter(
        field_name="syllabus__departments",
        queryset=Department.objects.all(),
    )
    schedules = django_filters.ModelMultipleChoiceFilter(
        field_name="schedules",
        queryset=Schedule.objects.all(),
        label="スケジュール",
    )
    day = django_filters.NumberFilter(
        field_name="schedules__day", lookup_expr="exact", label="曜日"
    )
    time = django_filters.NumberFilter(
        field_name="schedules__time", lookup_expr="exact", label="時限"
    )
    is_required = django_filters.BooleanFilter(field_name="syllabus__is_required")
    is_exam = django_filters.BooleanFilter(field_name="syllabus__is_exam")
    min_grade = django_filters.NumberFilter(
        field_name="grade", lookup_expr="gte", label="最小学年"
    )
    max_grade = django_filters.NumberFilter(
        field_name="grade", lookup_expr="lte", label="最大学年"
    )
    instructor = django_filters.CharFilter(
        field_name="instructor", lookup_expr="icontains", label="担当教員"
    )
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="講義名"
    )

    class Meta:
        model = Lecture
        fields = {
            "grade": ["exact"],
        }


class RegistrationFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name="year", lookup_expr="exact")
    number = django_filters.NumberFilter(method="filter_by_term")
    schedules = django_filters.ModelMultipleChoiceFilter(
        field_name="lecture__schedules",
        queryset=Schedule.objects.all(),
        label="スケジュール",
    )

    class Meta:
        model = Registration
        fields = ["year", "number"]

    def filter_by_term(self, queryset, name, value):
        """
        Registration の関連先 Lecture の terms の中で、
        number が指定された値に一致するものだけフィルタします。
        """
        return queryset.filter(lecture__terms__number=value).distinct()
