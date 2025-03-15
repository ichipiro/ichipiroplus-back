from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from accounts.models import Faculty, Department
from accounts.models import UserProfile
from accounts.constants import GRADE_FIRST, GRADE_SECOND


class UserProfileModelTest(TestCase):
    """UserProfileモデルのテスト"""

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

    def test_profile_creation(self):
        """ユーザープロフィールが正しく作成されるかテスト"""
        # ユーザー作成時にプロフィールが自動生成されることを確認
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertIsInstance(self.user.profile, UserProfile)

        # デフォルト値の検証
        self.assertFalse(self.user.profile.is_profile_complete)
        self.assertIsNotNone(
            self.user.profile.profile_id
        )  # user_idからprofile_idに変更した場合

    def test_profile_update(self):
        """プロフィール情報の更新が正しく機能するかテスト"""
        profile = self.user.profile
        profile.display_name = "テストユーザー"
        profile.faculty = self.faculty
        profile.department = self.department
        profile.grade = GRADE_FIRST
        profile.save()

        # 更新されたプロフィールを再取得
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.display_name, "テストユーザー")
        self.assertEqual(updated_profile.faculty, self.faculty)
        self.assertEqual(updated_profile.department, self.department)
        self.assertEqual(updated_profile.grade, GRADE_FIRST)

    def test_profile_id_uniqueness(self):
        """プロフィールIDの一意性をテスト"""
        profile1 = self.user.profile
        profile1.profile_id = "uniqueid123"  # user_idからprofile_idに変更した場合
        profile1.save()

        user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="password123"
        )
        profile2 = user2.profile
        profile2.profile_id = "uniqueid123"  # 同じIDを設定

        # 一意性制約違反で例外が発生するはず
        with self.assertRaises(IntegrityError):
            profile2.save()

    def test_check_profile_complete(self):
        """プロフィール完了チェック機能のテスト"""
        profile = self.user.profile

        # 不完全なプロフィール
        profile.display_name = "テストユーザー"
        profile.save()
        profile.check_profile_complete()
        self.assertFalse(profile.is_profile_complete)

        # 完全なプロフィール
        profile.faculty = self.faculty
        profile.department = self.department
        profile.grade = GRADE_SECOND
        profile.save()
        profile.check_profile_complete()
        self.assertTrue(profile.is_profile_complete)

    def test_cascade_delete(self):
        """ユーザー削除時のプロフィール削除をテスト"""
        user_id = self.user.id
        self.user.delete()

        # ユーザー削除後、関連するプロフィールも削除されていることを確認
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(user_id=user_id)
