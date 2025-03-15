import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    registration_id = django_filters.CharFilter(
        field_name="registration", lookup_expr="exact"
    )

    class Meta:
        model = Task
        fields = ["registration_id"]
