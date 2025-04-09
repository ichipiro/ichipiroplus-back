import os
import django
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


logger = logging.getLogger(__name__)
scheduler = BlockingScheduler()


def send_lecture_notification_job(time_slot):
    """講義通知を送信するジョブ"""
    logger.info(f"時限 {time_slot} の講義通知ジョブを実行します")
    try:
        call_command("send_lecture_notifications", time_slot=time_slot)
        logger.info(f"時限 {time_slot} の講義通知ジョブが完了しました")
    except Exception as e:
        logger.error(
            f"時限 {time_slot} の講義通知ジョブでエラーが発生しました: {str(e)}"
        )


def main():
    """スケジューラのメイン関数"""
    logger.info("スケジューラを開始します")

    # 1限
    scheduler.add_job(
        send_lecture_notification_job,
        CronTrigger(hour=9, minute=0, timezone="Asia/Tokyo"),
        args=[1],
        id="notify_first_period",
        replace_existing=True,
    )

    # 2限
    scheduler.add_job(
        send_lecture_notification_job,
        CronTrigger(hour=10, minute=40, timezone="Asia/Tokyo"),
        args=[2],
        id="notify_second_period",
        replace_existing=True,
    )

    # 3限
    scheduler.add_job(
        send_lecture_notification_job,
        CronTrigger(hour=13, minute=0, timezone="Asia/Tokyo"),
        args=[3],
        id="notify_third_period",
        replace_existing=True,
    )

    # 4限
    scheduler.add_job(
        send_lecture_notification_job,
        CronTrigger(hour=14, minute=40, timezone="Asia/Tokyo"),
        args=[4],
        id="notify_fourth_period",
        replace_existing=True,
    )

    # 5限
    scheduler.add_job(
        send_lecture_notification_job,
        CronTrigger(hour=16, minute=20, timezone="Asia/Tokyo"),
        args=[5],
        id="notify_fifth_period",
        replace_existing=True,
    )

    try:
        logger.info("スケジューラを開始しました")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("スケジューラを停止します")
        scheduler.shutdown()
        logger.info("スケジューラを停止しました")


if __name__ == "__main__":
    main()
