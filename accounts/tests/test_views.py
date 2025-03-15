from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from accounts.models import Faculty, Department
from accounts.models import UserProfile
from accounts.constants import GRADE_FIRST, GRADE_SECOND


class ProfileViewTest(TestCase):
    """ProfileViewのテスト"""

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

        # APIクライアントのセットアップ
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # プロフィールビューのURL
        self.url = reverse("profile-detail")

    def test_get_profile(self):
        """プロフィール情報の取得テスト"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # レスポンスの内容確認
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertFalse(response.data["is_profile_complete"])

    def test_update_profile(self):
        """プロフィール情報の更新テスト"""
        data = {
            "display_name": "更新後ユーザー",
            "faculty_id": self.faculty.id,
            "department_id": self.department.id,
            "grade": GRADE_FIRST,
        }

        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 更新されたプロフィールを再取得
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.display_name, "更新後ユーザー")
        self.assertEqual(updated_profile.faculty, self.faculty)
        self.assertEqual(updated_profile.department, self.department)
        self.assertEqual(updated_profile.grade, GRADE_FIRST)

        # プロフィール完了状態の確認
        self.assertTrue(updated_profile.is_profile_complete)

    def test_partial_update_profile(self):
        """プロフィール情報の部分更新テスト"""
        # まず基本データを設定
        self.user.profile.display_name = "テストユーザー"
        self.user.profile.faculty = self.faculty
        self.user.profile.department = self.department
        self.user.profile.grade = GRADE_FIRST
        self.user.profile.save()

        # 学年だけを更新
        data = {"grade": GRADE_SECOND}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 更新されたプロフィールを再取得
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.grade, GRADE_SECOND)
        self.assertEqual(updated_profile.display_name, "テストユーザー")  # 変更なし

    def test_unauthenticated_access(self):
        """未認証アクセスのテスト"""
        # 未認証クライアントの作成
        unauthenticated_client = APIClient()

        response = unauthenticated_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
