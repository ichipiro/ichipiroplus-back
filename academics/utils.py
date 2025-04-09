from django.utils import timezone
from .models import Term
from django.db.models import Q


def get_current_term_and_year():
    """
    現在のタームと年度を取得する共通関数

    Returns:
        tuple: (現在のターム, 年度) のタプル、タームが見つからない場合は (None, None)
    """
    today = timezone.now().date()

    current_term = Term.objects.filter(
        Q(start_date__lte=today) & Q(end_date__gte=today)
    ).first()

    # 該当するタームがない場合は None を返す
    if not current_term:
        return None, None

    end_date = current_term.end_date
    fiscal_year = end_date.year

    # 1月〜3月の場合は前年度として扱う
    if end_date.month <= 3:
        fiscal_year -= 1

    return current_term, fiscal_year
