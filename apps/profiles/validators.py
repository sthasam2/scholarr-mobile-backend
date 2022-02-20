import datetime as dt

import pytz
from configs.definitions import TIME_ZONE
from django.core.exceptions import ValidationError


def validate_date_lt_today(value):
    """ """
    now_naive = dt.datetime.now()
    now_aware = pytz.timezone(TIME_ZONE).localize(now_naive)

    if value > now_aware:
        raise ValidationError(
            f"Datetime can not be greater than present Datetime",
            "\n",
            f"Entered Datetime: {value.strftieme('%d %B, %Y %I:%M%p')}",
            "\n",
            f"Current Datetime: {dt.datetime.now()}",
        )
