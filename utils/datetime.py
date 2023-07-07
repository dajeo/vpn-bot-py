from datetime import datetime

from babel.dates import format_date
from dateutil.relativedelta import relativedelta


def translate_date(d: datetime) -> str:
    expired_at = d + relativedelta(months=2)
    return format_date(expired_at, format="long", locale="ru")
