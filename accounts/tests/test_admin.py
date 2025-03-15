from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Faculty, Department
from accounts.constants import GRADE_FIRST


class AdminSiteTest(TestCase):
    """管理サイトのテスト"""

    def setUp(self):
        # 管理者ユーザーの作成
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        # テスト用データのセットアップ
        self.faculty = Faculty.objects.create(name="情報科学部")
        self.department = Department.objects.create(
            name="情報工学科", faculty=self.faculty
        )

        # 一般ユーザーの作成
        self.test_user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        # プロフィール情報の設定
        self.test_user.profile.display_name = "テストユーザー"
        self.test_user.profile.faculty = self.faculty
        self.test_user.profile.department = self.department
        self.test_user.profile.grade = GRADE_FIRST
        self.test_user.profile.save()

        # ログイン
        self.client.login(username="admin", password="adminpass123")

        # 管理サイトのURLを設定
        self.user_changelist_url = reverse("admin:auth_user_changelist")
        self.user_change_url = reverse(
            "admin:auth_user_change", args=[self.test_user.id]
        )

    def test_user_changelist(self):
        """ユーザー一覧ページが正しく表示されるかテスト"""
        response = self.client.get(self.user_changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_user.username)

    def test_user_change_form(self):
        """ユーザー詳細ページでプロフィール情報が表示されるかテスト"""
        response = self.client.get(self.user_change_url)
        self.assertEqual(response.status_code, 200)

        # プロフィールフィールドが表示されているか確認
        self.assertContains(response, "display_name")
        self.assertContains(response, "faculty")
        self.assertContains(response, "department")
        self.assertContains(response, "grade")
