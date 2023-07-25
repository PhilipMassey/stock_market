import market_data as md
import pandas as pd
import numpy as np
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
client = MongoClient()
db = client['stock_market']


def df_add_date_column(ndays, df):
    strdt = md.get_mdb_strdate_for_ndays(ndays)
    dt = md.get_mdbdate_from_strdate(strdt)
    df['Date'] = dt


def df_idxdate_tostr(df):
    d = df.index.values[0]
    return np.datetime_as_string(d, timezone='UTC')[:10]

def df_idxdate_to_mdbdate(df):
    ts = df.index.values[0]
    dt= pd.to_datetime(str(ts))
    timestring = dt.strftime('%Y-%m-%d')
    return get_mdbdate_from_strdate(timestring)

def get_mdbdate_from_strdate(strDate):
    return datetime.strptime(strDate, '%Y-%m-%d')

def get_date_for_mdb(ndays):
    strDate = md.get_busdate_ndays_ago(ndays)
    return datetime.strptime(strDate, '%Y-%m-%d')

def get_date_for_ndays(ndays):
    dt = get_date_for_mdb(ndays)
    return f'{dt:%b %-d}'

def get_mdb_strdate_for_ndays(ndays):
    dt = get_date_for_mdb(ndays)
    return f'{dt:%Y-%m-%d}'

def get_pd_time_series_for_ndays(ndays):
    strdate = md.get_busdate_ndays_ago(ndays)
    return pd.Timestamp(strdate)

def dateindex_as_ddmmm(dt):
    strdt = np.datetime_as_string(dt, unit='D')
    dt = datetime.strptime(strdt, '%Y-%m-%d')
    return f'{dt:%b %-d}'

def count_mdb_on_date(ndays,symbol,db_coll_name):
    adate = md.get_date_for_mdb(ndays)
    db_coll = db[db_coll_name]
    return db_coll.count_documents({'Date': adate, 'symbol':symbol})


def count_mdb_symbol_detween_dates(ndays,period,symbol,db_coll_name):
    start_date, end_date = md.get_ndate_and_todate(ndays,period)
    start_date, end_date = md.get_mdbdate_from_strdate(start_date),md.get_mdbdate_from_strdate(end_date)
    db_coll = db[db_coll_name]
    return db_coll.count_documents({'Date': {'$lte':end_date, '$gte':start_date}, 'symbol':symbol})


def df_add_date_index(ndays,df):
    strdt = md.get_mdb_strdate_for_ndays(ndays)
    dt = md.get_mdbdate_from_strdate(strdt)
    df['Date'] = dt
    df.set_index('Date',inplace=True)
    return df

