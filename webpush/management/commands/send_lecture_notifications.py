from django.core.management.base import BaseCommand
from django.utils import timezone
from academics.constants import TIME_SLOTS
from academics.models import Registration, Schedule
from academics.utils import get_current_term_and_year
from webpush.views import send_push_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "講義の開始時間に通知を送信するコマンド"

    def add_arguments(self, parser):
        # オプションで特定の時限を指定できるようにする
        parser.add_argument("--time-slot", type=int, help="通知する時限 (1-5)")

    def handle(self, *args, **options):
        now = timezone.now()
        day_of_week = now.weekday() + 1

        # 土日は通知しない
        if day_of_week > 5:  # 6=土曜, 7=日曜
            self.stdout.write("土日は講義通知を送信しません")
            return

        current_time_slot = options.get("time_slot")

        if not current_time_slot:
            self.stdout.write("指定された時限がありません")
            return

        current_term, fiscal_year = get_current_term_and_year()

        if not current_term or not fiscal_year:
            self.stdout.write("現在のタームが見つかりません")
            return

        self.stdout.write(
            f"実行日時: {now}, 曜日: {day_of_week}, 時限: {current_time_slot}"
        )
        self.stdout.write(f"年度: {fiscal_year}, ターム: {current_term.number}")

        # 該当する講義のスケジュールを取得
        schedule_ids = Schedule.objects.filter(
            day=day_of_week, time=current_time_slot
        ).values_list("id", flat=True)

        if not schedule_ids:
            self.stdout.write("該当するスケジュールはありません")
            return

        # 該当する登録情報を取得（現在のタームも考慮）
        registrations = (
            Registration.objects.filter(
                lecture__schedules__id__in=schedule_ids,
                lecture__terms__number=current_term.number,  # 現在のタームの講義のみ
                year=fiscal_year,
            )
            .select_related("user", "lecture")
            .distinct()
        )

        self.stdout.write(f"通知対象の登録数: {registrations.count()}")

        # 各ユーザーに通知を送信
        success_count = 0
        failed_count = 0

        for registration in registrations:
            user = registration.user
            lecture = registration.lecture

            # 講義開始通知の送信
            time_info = TIME_SLOTS[current_time_slot]
            title = f"出席を登録しよう！"
            body = f"{lecture.name}（{time_info['start']}〜{time_info['end']}）が {lecture.room or '未設定'} で始まります"
            url = f"/timetable/{fiscal_year}/{current_term.number}/{(day_of_week - 1) * 5 + current_time_slot}"

            result = send_push_notification(
                user=user, title=title, body=body, url=url, notification_type="lecture"
            )

            success_count += result["success"]
            failed_count += result["failed"]

            self.stdout.write(
                f"ユーザー {user.username} への通知: 成功={result['success']}, 失敗={result['failed']}"
            )

        self.stdout.write(f"通知送信完了: 成功={success_count}, 失敗={failed_count}")
