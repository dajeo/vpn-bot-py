from datetime import datetime

from babel.dates import format_date
from dateutil.relativedelta import relativedelta


def add_days(d: datetime, days: int) -> datetime:
    return d + relativedelta(days=days)


def remove_days(d: datetime, days: int) -> datetime:
    return d - relativedelta(days=days)


def add_months(d: datetime, months: int) -> datetime:
    return d + relativedelta(months=months)


def translate_date(d: datetime) -> str:
    expired_at = add_months(d, 2)
    return format_date(expired_at, format="long", locale="ru")
