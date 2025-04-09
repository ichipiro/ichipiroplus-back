import uuid
from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import User

from academics.constants import DAY_CHOICES, MAX_TIME, TERM_CHOICES, TIME_CHOICES
from accounts.models import Department


class Term(models.Model):
    number = models.PositiveSmallIntegerField(
        choices=TERM_CHOICES, verbose_name="ターム", primary_key=True
    )
    start_date = models.DateField(verbose_name="開始日", null=True, blank=True)
    end_date = models.DateField(verbose_name="終了日", null=True, blank=True)

    class Meta:
        verbose_name = "ターム"
        verbose_name_plural = "学期"

    def __str__(self):
        return f"第{self.number}ターム"

    def clean(self):
        if self.number not in dict(TERM_CHOICES):
            raise ValidationError(
                {"number": "タームは1から4の間でなければなりません。"}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Schedule(models.Model):
    day = models.PositiveSmallIntegerField(choices=DAY_CHOICES, verbose_name="曜日")
    time = models.PositiveSmallIntegerField(choices=TIME_CHOICES, verbose_name="時限")
    id = models.PositiveSmallIntegerField(primary_key=True, editable=False)

    class Meta:
        unique_together = ("day", "time")
        verbose_name = "スケジュール"
        verbose_name_plural = "スケジュール"

    def __str__(self):
        return f"{dict(DAY_CHOICES).get(self.day)} {dict(TIME_CHOICES).get(self.time)}"

    def save(self, *args, **kwargs):
        # dayとtimeの組み合わせから一意なIDを計算
        self.id = (self.day - 1) * MAX_TIME + self.time
        super().save(*args, **kwargs)


class Syllabus(models.Model):
    id = models.CharField(max_length=36, primary_key=True, verbose_name="シラバスID")
    name = models.CharField(max_length=300, verbose_name="講義名")
    units = models.FloatField(verbose_name="単位数", default=0)
    schedules = models.ManyToManyField(
        Schedule,
        related_name="syllabuses",
        verbose_name="スケジュール",
        blank=True,
    )
    instructor = models.CharField(max_length=300, verbose_name="担当教員", blank=True)
    grade = models.CharField(verbose_name="対象学年", blank=True)
    purpose = models.TextField(verbose_name="講義の目的", blank=True)
    goal = models.TextField(verbose_name="到達目標", blank=True)
    is_required = models.BooleanField(verbose_name="必修", default=False)
    is_exam = models.BooleanField(verbose_name="期末テスト", default=False)
    description = models.TextField(max_length=5000, blank=True, verbose_name="概要")
    eval_method = models.TextField(max_length=1000, blank=True, verbose_name="評価方法")
    departments = models.ManyToManyField(
        Department, related_name="syllabuses", verbose_name="履修可能学科"
    )
    textbook = models.TextField(verbose_name="教科書等", blank=True)
    feedback = models.TextField(
        verbose_name="課題や試験に対するフィードバック", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"{self.id}-{self.name}"

    class Meta:
        verbose_name_plural = "シラバス"


class Lecture(models.Model):
    id = models.CharField(
        max_length=36,
        primary_key=True,
        default=uuid.uuid4,
        verbose_name="講義コード",
    )
    syllabus = models.ForeignKey(  # シラバスID
        Syllabus,
        related_name="lectures",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="シラバスコード",
    )
    name = models.CharField(max_length=200, verbose_name="講義名")  # 講義名
    room = models.CharField(max_length=50, blank=True, verbose_name="講義室")  # 講義室
    terms = models.ManyToManyField(Term, related_name="lectures", verbose_name="ターム")
    grade = models.IntegerField(verbose_name="対象学年", default=1)
    schedules = models.ManyToManyField(
        Schedule, related_name="lectures", verbose_name="スケジュール"
    )
    instructor = models.CharField(max_length=200, verbose_name="担当教員")
    biko = models.CharField(max_length=300, blank=True, verbose_name="備考")

    is_public = models.BooleanField(default=True)  # 他の人が見えるかどうか
    is_public_editable = models.BooleanField(default=True)  # 他の人が編集可能かどうか
    owner = models.ForeignKey(  # 講義制作者
        User,
        related_name="lectures",
        on_delete=models.CASCADE,
        verbose_name="所有者",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name_plural = "講義"

    def __str__(self):
        return f"{self.id} - {self.name}"


class Registration(models.Model):
    user = models.ForeignKey(
        User,
        related_name="registrations",
        on_delete=models.CASCADE,
        verbose_name="ユーザー",
    )
    lecture = models.ForeignKey(
        Lecture,
        related_name="registrations",
        on_delete=models.CASCADE,
        verbose_name="講義",
    )
    year = models.PositiveIntegerField(verbose_name="年度")
    attendance_count = models.PositiveSmallIntegerField(
        default=0, verbose_name="出席回数"
    )
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    class Meta:
        unique_together = ("user", "lecture", "year")
        verbose_name_plural = "登録状況"

    def increment_attendance(self):
        if self.attendance_count < 15:
            self.attendance_count += 1
            self.save()
        return self.attendance_count

    def decrement_attendance(self):
        if self.attendance_count > 0:
            self.attendance_count -= 1
            self.save()
        return self.attendance_count

    def __str__(self):
        return f"{self.user.profile.display_name} が {self.lecture.name} を {self.year}年  に登録"
