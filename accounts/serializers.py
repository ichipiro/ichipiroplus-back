from rest_framework import serializers
from .models import Faculty, Department
from common.exceptions import BusinessLogicError, ValidationError
from .models import UserProfile
from django.contrib.auth.models import User


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ["id", "name"]


class DepartmentSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = Department
        fields = ["id", "name", "faculty"]


class UserProfileSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)
    faculty_id = serializers.PrimaryKeyRelatedField(
        queryset=Faculty.objects.all(),
        write_only=True,
        source="faculty",
        required=False,
        allow_null=True,
    )
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        write_only=True,
        source="department",
        required=False,
        allow_null=True,
    )
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "profile_id",
            "display_name",
            "email",
            "introduction",
            "faculty",
            "faculty_id",
            "department",
            "department_id",
            "grade",
            "picture",
            "is_profile_complete",
        ]
        read_only_fields = ["is_profile_complete"]

    def validate_user_id(self, value):
        # 文字数チェック
        if len(value) < 4:
            # カスタムエラークラスを使用
            raise ValidationError("ユーザーIDは4文字以上である必要があります")

        # ユニーク性チェック
        if (
            UserProfile.objects.exclude(pk=self.instance.pk if self.instance else None)
            .filter(user_id=value)
            .exists()
        ):
            raise ValidationError("このユーザーIDは既に使用されています")

        return value

    def validate(self, data):
        faculty = data.get("faculty")
        department = data.get("department")

        # 学部と学科の整合性チェック
        if faculty and department and department.faculty != faculty:
            raise BusinessLogicError(
                {"department": "選択された学科は選択された学部に属していません"}
            )

        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # プロフィール完了状態を確認して更新
        instance.check_profile_complete()
        instance.save()
        return instance


class UserWithProfileSerializer(serializers.ModelSerializer):

    # プロフィール情報をネストして表示
    profile_id = serializers.CharField(source="profile.profile_id", read_only=True)
    display_name = serializers.CharField(source="profile.display_name", read_only=True)
    introduction = serializers.CharField(source="profile.introduction", read_only=True)
    faculty = FacultySerializer(source="profile.faculty", read_only=True)
    department = DepartmentSerializer(source="profile.department", read_only=True)
    grade = serializers.IntegerField(source="profile.grade", read_only=True)
    picture = serializers.CharField(source="profile.picture", read_only=True)
    is_profile_complete = serializers.BooleanField(
        source="profile.is_profile_complete", read_only=True
    )

    class Meta:
        model = User
        fields = [
            "introduction",
            "profile_id",
            "display_name",
            "faculty",
            "department",
            "grade",
            "picture",
            "is_profile_complete",
        ]
