import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
from datetime import datetime
from dateutil.relativedelta import relativedelta

import market_data

nyse = mcal.get_calendar("NYSE")

def get_busdate_ndays_ago(ndays):
    strdate = '{:%Y-%m-%d}'.format(datetime.now())
    dt = np.busday_offset(dates=strdate, offsets=-ndays, roll='backward', holidays=nyse.holidays().holidays)
    return str(dt)


def get_nbusdays_from_datestr(datestr):
    dtnow = '{:%Y-%m-%d}'.format(datetime.now())
    bus_dtnow = np.busday_offset(dates=dtnow, offsets=0, roll='backward', holidays=nyse.holidays().holidays)
    dt = str(bus_dtnow)
    nbdays =  np.busday_count(datestr, dt, holidays=nyse.holidays().holidays)
    return nbdays


def get_nbusdays_from_date(date):
    datestr = f'{date:%Y-%m-%d}'
    dtnow = '{:%Y-%m-%d}'.format(datetime.now())
    bus_dtnow = np.busday_offset(dates=dtnow, offsets=0, roll='backward', holidays=nyse.holidays().holidays)
    dt = str(bus_dtnow)
    nbdays =  np.busday_count(datestr, dt, holidays=nyse.holidays().holidays)
    return nbdays


def get_ndays_for_end():
    today = f'{datetime.now():%Y-%m-%d}'
    days = nyse.valid_days(start_date=today, end_date=today)
    return len(days)

def isit_weekend():
    return get_ndays_for_end() == 0



def get_ndays_periods(months=[],weeks=[],days=[]):
    last_day = get_ndays_for_end()
    now = datetime.now()
    periods = []
    for idx in months:
        periods.append(get_nbusdays_from_date(now - relativedelta(months=idx)))
    for idx in weeks:
        periods.append(get_nbusdays_from_date(now - relativedelta(weeks=idx)))
    for idx in days:
        periods.append(get_nbusdays_from_date(now - relativedelta(days=idx)))
        periods = sorted(list(set(periods)),reverse=True)
    if len(days) == 0:
        periods.append(last_day)
    return tuple(periods)


def get_desc_date(dfRow):
    date = pd.to_datetime(dfRow.index.values[0])
    return calendar.day_name[date.weekday()]+' '+'{:%Y-%m-%d}'.format(date)


def get_ndate_and_todate(ndays, period):
    strdate = get_busdate_ndays_ago(ndays+period)
    enddate = get_busdate_ndays_ago(ndays)
    return strdate,enddate


def get_ndate_and_prevdate(ndays):
    strdate = get_busdate_ndays_ago(ndays + 1)
    enddate = get_busdate_ndays_ago(ndays)
    return strdate,enddate



