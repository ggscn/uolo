from datetime import datetime, date, timedelta
import pytz
from dateutil.relativedelta import relativedelta

def now_utc():
    return datetime.now(pytz.utc)

def today_utc():
    return date.today(pytz.utc)

def get_previous_month(months):
    return date.today() - relativedelta(months=months)
