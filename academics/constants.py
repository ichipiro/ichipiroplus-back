# 学期に関する定数
TERM_SPRING = 1
TERM_SUMMER = 2
TERM_FALL = 3
TERM_WINTER = 4

TERM_CHOICES = [
    (TERM_SPRING, "第1ターム(春)"),
    (TERM_SUMMER, "第2ターム(夏)"),
    (TERM_FALL, "第3ターム(秋)"),
    (TERM_WINTER, "第4ターム(冬)"),
]

# 曜日に関する定数
DAY_MONDAY = 1
DAY_TUESDAY = 2
DAY_WEDNESDAY = 3
DAY_THURSDAY = 4
DAY_FRIDAY = 5
DAY_SATURDAY = 6
DAY_SUNDAY = 7

DAY_CHOICES = [
    (DAY_MONDAY, "月曜日"),
    (DAY_TUESDAY, "火曜日"),
    (DAY_WEDNESDAY, "水曜日"),
    (DAY_THURSDAY, "木曜日"),
    (DAY_FRIDAY, "金曜日"),
    (DAY_SATURDAY, "土曜日"),
    (DAY_SUNDAY, "日曜日"),
]

# 時限に関する定数
TIME_FIRST = 1
TIME_SECOND = 2
TIME_THIRD = 3
TIME_FOURTH = 4
TIME_FIFTH = 5
MAX_TIME = 5

TIME_CHOICES = [
    (TIME_FIRST, "1限"),
    (TIME_SECOND, "2限"),
    (TIME_THIRD, "3限"),
    (TIME_FOURTH, "4限"),
    (TIME_FIFTH, "5限"),
]

# 各時限の実際の時間
TIME_SLOTS = {
    TIME_FIRST: {"start": "09:00", "end": "10:30"},
    TIME_SECOND: {"start": "10:40", "end": "12:10"},
    TIME_THIRD: {"start": "13:00", "end": "14:30"},
    TIME_FOURTH: {"start": "14:40", "end": "16:10"},
    TIME_FIFTH: {"start": "16:20", "end": "17:50"},
}
