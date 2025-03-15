from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile


class SignalsTest(TestCase):
    """シグナルのテスト"""

    def test_profile_auto_create(self):
        """ユーザー作成時にプロフィールが自動作成されるかテスト"""
        # ユーザーを作成
        user = User.objects.create_user(
            username="signaltest", email="signal@example.com", password="password123"
        )

        # プロフィールが自動的に作成されたか確認
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, UserProfile)

    def test_profile_not_duplicated(self):
        """プロフィールが重複して作成されないことを確認"""
        # ユーザーを作成
        user = User.objects.create_user(
            username="duplicatetest",
            email="duplicate@example.com",
            password="password123",
        )

        # プロフィール数を確認
        profile_count = UserProfile.objects.filter(user=user).count()
        self.assertEqual(profile_count, 1)

        # ユーザーを更新してシグナルを再発火
        user.username = "duplicatetest_updated"
        user.save()

        # プロフィール数が増えていないことを確認
        profile_count_after = UserProfile.objects.filter(user=user).count()
        self.assertEqual(profile_count_after, 1)
