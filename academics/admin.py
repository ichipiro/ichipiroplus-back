from import_export import resources, fields
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Department, Syllabus
from .models import Lecture, Registration, Schedule, Term
from import_export.widgets import ManyToManyWidget


class SyllabusResource(resources.ModelResource):
    schedules = fields.Field(
        column_name="schedules",
        attribute="schedules",
        widget=ManyToManyWidget(Schedule, field="id", separator=";"),
    )
    departments = fields.Field(
        column_name="departments",
        attribute="departments",
        widget=ManyToManyWidget(Department, field="name", separator=";"),
    )

    class Meta:
        model = Syllabus
        fields = (
            "id",
            "name",
            "units",
            "schedules",
            "instructor",
            "grade",
            "type",
            "purpose",
            "goal",
            "departments",
            "is_required",
            "is_exam",
            "description",
            "eval_method",
            "textbook",
            "feedback",
        )
        import_id_fields = ("id",)
        skip_unchanged = True
        report_skipped = True


class LectureResource(resources.ModelResource):
    terms = fields.Field(
        column_name="terms",
        attribute="terms",
        widget=ManyToManyWidget(Term, field="number", separator=";"),
    )
    schedules = fields.Field(
        column_name="schedules",
        attribute="schedules",
        widget=ManyToManyWidget(Schedule, field="id", separator=";"),
    )

    class Meta:
        model = Lecture
        fields = (
            "id",
            "syllabus",
            "name",
            "terms",
            "schedules",
            "grade",
            "room",
            "instructor",
            "units",
            "biko",
            "owner",
        )
        import_id_fields = ("id",)
        skip_unchanged = True
        report_skipped = True


@admin.register(Lecture)
class LectureAdmin(ImportExportModelAdmin):
    resource_class = LectureResource
    filter_horizontal = ("terms", "schedules")


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("number", "start_date", "end_date")


@admin.register(Syllabus)
class SyllabusAdmin(ImportExportModelAdmin):
    resource_class = SyllabusResource
    filter_horizontal = ("schedules",)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "lecture", "attendance_count", "registered_at")
    date_hierarchy = "registered_at"
