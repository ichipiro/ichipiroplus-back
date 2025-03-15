from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from accounts.models import Faculty, Department
from accounts.models import UserProfile
from accounts.serializers import UserProfileSerializer, UserWithProfileSerializer
from accounts.constants import GRADE_FIRST


class UserProfileSerializerTest(TestCase):
    """UserProfileSerializerのテスト"""

    def setUp(self):
        # テスト用データのセットアップ
        self.faculty = Faculty.objects.create(name="情報科学部")
        self.department = Department.objects.create(
            name="情報工学科", faculty=self.faculty
        )
        self.another_faculty = Faculty.objects.create(name="国際学部")
        self.another_department = Department.objects.create(
            name="国際学科", faculty=self.another_faculty
        )

        # テストユーザーの作成
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        # プロフィール情報の設定
        self.profile = self.user.profile
        self.profile.display_name = "テストユーザー"
        self.profile.faculty = self.faculty
        self.profile.department = self.department
        self.profile.grade = GRADE_FIRST
        self.profile.save()

    def test_serialization(self):
        """シリアライズが正しく機能するかテスト"""
        serializer = UserProfileSerializer(instance=self.profile)
        data = serializer.data

        self.assertEqual(data["display_name"], "テストユーザー")
        self.assertEqual(data["faculty"]["name"], "情報科学部")
        self.assertEqual(data["department"]["name"], "情報工学科")
        self.assertEqual(data["grade"], GRADE_FIRST)
        self.assertEqual(
            data["email"], "test@example.com"
        )  # UserのEmailがプロフィールで表示されるか

    def test_deserialization_valid_data(self):
        """有効なデータによる逆シリアライズのテスト"""
        data = {
            "display_name": "更新後ユーザー",
            "faculty_id": self.another_faculty.id,
            "department_id": self.another_department.id,
            "grade": GRADE_FIRST,
        }

        serializer = UserProfileSerializer(instance=self.profile, data=data)
        self.assertTrue(serializer.is_valid())

        updated_profile = serializer.save()
        self.assertEqual(updated_profile.display_name, "更新後ユーザー")
        self.assertEqual(updated_profile.faculty, self.another_faculty)
        self.assertEqual(updated_profile.department, self.another_department)

    def test_deserialization_invalid_data(self):
        """無効なデータによる逆シリアライズのテスト"""
        # 学部と学科が不一致のデータ
        data = {
            "display_name": "更新後ユーザー",
            "faculty_id": self.faculty.id,
            "department_id": self.another_department.id,  # 異なる学部の学科
            "grade": GRADE_FIRST,
        }

        serializer = UserProfileSerializer(instance=self.profile, data=data)

        try:
            # バリデーションでエラーになるはず
            serializer.is_valid()
            self.fail("BusinessLogicErrorが発生するはずですが、発生しませんでした")
        except Exception as e:
            # 例外のメッセージに 'department' が含まれることを確認
            self.assertIn("department", str(e))


class UserWithProfileSerializerTest(TestCase):
    """UserWithProfileSerializerのテスト"""

    def setUp(self):
        # テスト用データのセットアップ
        self.faculty = Faculty.objects.create(name="情報科学部")
        self.department = Department.objects.create(
            name="情報工学科", faculty=self.faculty
        )

        # テストユーザーの作成
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        # プロフィール情報の設定
        self.profile = self.user.profile
        self.profile.display_name = "テストユーザー"
        self.profile.faculty = self.faculty
        self.profile.department = self.department
        self.profile.grade = GRADE_FIRST
        self.profile.save()

    def test_user_with_profile_serialization(self):
        """ユーザーとプロフィール情報が一緒にシリアライズされるかテスト"""
        serializer = UserWithProfileSerializer(instance=self.user)
        data = serializer.data

        # ユーザー情報の検証
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")

        # プロフィール情報の検証
        self.assertEqual(data["display_name"], "テストユーザー")
        self.assertEqual(data["faculty"]["name"], "情報科学部")
        self.assertEqual(data["department"]["name"], "情報工学科")
        self.assertEqual(data["grade"], GRADE_FIRST)
