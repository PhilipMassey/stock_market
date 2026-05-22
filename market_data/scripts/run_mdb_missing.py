#!/usr/bin/env python
# coding: utf-8

import market_data as md
from datetime import datetime
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
import sys
import yfinance as yf

nyse = mcal.get_calendar("NYSE")
import pytz


schedule = md.get_schedule()
from_date = schedule[0]
to_date = schedule[-1]
# '{:%Y-%m-%d %H %A}'.format(from_date),'{:%Y-%m-%d %H %A}'.format(to_date)
business_days = md.get_business_days(schedule)
print("Business days from :", business_days[-1], " to ", business_days[0])
print(f"Total: {len(business_days)}\n")

def get_yahoo_ndays_ago(bday, symbols):
    # df = yf.download(tickers=symbols, interval="1d", start=from_date, end=to_date, group_by='column',        auto_adjust=True, prepost=True, threads=True)
    df = yf.download(symbols, start=bday, end=bday + timedelta(days=1), auto_adjust=True, progress=False)
    # df = df.dropna(axis=1, how='all')
    if df.size == 0:
        print('no results from yahoo')
        return df
    return df[['Close']]

def to_dt(d):
    return datetime(d.year, d.month, d.day)


def get_df_from_mdb_for_bbay(bday, coll_name, symbols='', incl='', dateidx=True):
    from market_data.stock_mdb.mongo_connection_manager import get_mongo_database
    db = get_mongo_database(md.db_client)
    db_coll = db[coll_name]
    adate = to_dt(bday)
    df = pd.DataFrame({})
    if len(incl) != 0:
        symbols = md.get_symbols(incl)
    if db_coll.count_documents({'Date': adate}) > 0:
        if len(symbols) > 0:
            symbols.append('Date')  # Date field to be included in mdb results
            mdb_data = db_coll.find({'Date': adate}, symbols)
            symbols.remove('Date')
        else:
            mdb_data = db_coll.find({'Date': adate})
        df = md.mdb_to_df(mdb_data, dateidx)
    # print('mdb records {} for {} symbols on {}'.format(df.size,len(symbols),adate),end=', ')
    return df


bday = business_days[2]
symbols = md.get_symbols(md.all)
df = get_df_from_mdb_for_bbay(bday, md.db_close, symbols, '')
df


# In[9]:


def get_nbusdays_from_date(date):
    datestr = f'{date:%Y-%m-%d}'
    dtnow = '{:%Y-%m-%d}'.format(md.get_ny_now())
    bus_dtnow = np.busday_offset(dates=dtnow, offsets=0, roll='backward', holidays=nyse.holidays().holidays)
    dt = str(bus_dtnow)
    nbdays = np.busday_count(datestr, dt, holidays=nyse.holidays().holidays)
    return nbdays


def mdb_document_count(bday, db_coll_name):
    adate = to_dt(bday)
    db_coll = db[db_coll_name]
    return db_coll.count_documents({'Date': adate})


def get_missing_market_row(bday, symbols, load_missing_failed):
    dbaction = None
    df_missing = pd.DataFrame({})
    missing_symbols = []
    df_mdb = get_df_from_mdb_for_bbay(bday, md.db_close, symbols)
    if df_mdb.size == 0:  # missing whole row of data or missing symbols missing values 'Nan'
        count = mdb_document_count(bday, md.db_close)
        if count == 0:
            dbaction = 'ADD'
        else:
            dbaction = 'UPDATE'
        missing_symbols = symbols
    else:
        mdb_columns = set(df_mdb.columns)
        missing_symbols = set(symbols).difference(mdb_columns)
        if len(missing_symbols) > 0:
            dbaction = 'UPDATE'
    if len(missing_symbols) > 0:
        print(bday, dbaction, list(missing_symbols)[0:3], '....')
        df_missing = get_yahoo_ndays_ago(bday, missing_symbols)
        df_missing = df_missing.dropna(axis=1, how='all')

        if 'Close' in df_missing:
            close_df = df_missing['Close']
            if isinstance(close_df, pd.DataFrame):
                yahoo_symbols = close_df.columns.values
            else:
                # If it's a Series (single ticker), the data exists for the requested symbol
                yahoo_symbols = list(missing_symbols)

            for el in missing_symbols:
                if el not in yahoo_symbols:
                    load_missing_failed.append(el)
        else:
            for el in missing_symbols:
                load_missing_failed.append(el)
            df_missing = pd.DataFrame()  # Empty dataframe prevents downstream KeyError

    return (df_missing, dbaction, symbols)


def mdb_add_df(df, db_coll_name):
    data_dict = df.to_dict("records")
    db_coll = db[db_coll_name]
    result = db_coll.insert_many(data_dict)
    return len(result.inserted_ids)


def add_df_to_db(df, db_coll_name, dropidx=False):
    df = df.copy(deep=True)

    # 1. Flatten MultiIndex columns if they exist (drops the 'Close' layer)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(1)

    df.drop_duplicates(inplace=True)
    df.reset_index(inplace=True)

    # 2. Fix: Use a list ['Date'] or ['index'] to drop the index column safely
    if dropidx == True:
        # yfinance index is named 'Date'. When reset, it becomes a column named 'Date'
        # If it falls back to a standard range index, it becomes 'index'
        target_col = 'Date' if 'Date' in df.columns else 'index'
        df.drop(columns=[target_col], inplace=True, errors='ignore')

    return mdb_add_df(df, db_coll_name)


def df_idxdate_to_mdbdate(df):
    ts = df.index.values[0]
    dt = pd.to_datetime(str(ts))
    timestring = dt.strftime('%Y-%m-%d')
    return get_mdbdate_from_strdate(timestring)


def get_mdbdate_from_strdate(strDate):
    return datetime.strptime(strDate, '%Y-%m-%d')


def update_mdb_with_dfrow(df_m, coll_name):
    db_coll = db[coll_name]
    dt = df_idxdate_to_mdbdate(df_m)

    if df_m.size > 0:
        df_mc = df_m.copy(deep=True)

        # 1. FIX: Flatten the MultiIndex columns if they exist
        if isinstance(df_mc.columns, pd.MultiIndex):
            # level 1 contains the actual ticker names ('AAAU', 'ABBNY', etc.)
            df_mc.columns = df_mc.columns.get_level_values(1)

        df_mc = df_mc.dropna(axis='columns')
        df_mc.reset_index(inplace=True)

        # 2. Now 'Date' is a normal string column, so this drop will work perfectly
        df_mc.drop(columns=['Date'], inplace=True, errors='ignore')

        data_dict = df_mc.to_dict("records")

        if data_dict:  # Ensure data_dict is not empty after dropping NaNs
            newvalues = {"$set": data_dict[0]}
            query = {'Date': dt}
            result = db_coll.update_one(query, newvalues)


def update_mdb_with_missing_row(bday, symbols, load_missing_failed):
    print(format(bday), end=', ')
    df_m, dbaction, symbols = get_missing_market_row(bday, symbols, load_missing_failed)
    if df_m.size > 0:
        print(int(df_m.size), dbaction, end=', ')
        if dbaction == 'ADD':
            add_df_to_db(df_m, md.db_close)
        elif dbaction == 'UPDATE':
            update_mdb_with_dfrow(df_m, md.db_close)
    return symbols


def run_mdb_missing(symbols, business_days):
    load_missing_failed = []
    for bday in business_days:
        failed_count_before = len(load_missing_failed)
        symbols = update_mdb_with_missing_row(bday, symbols, load_missing_failed)

        newly_failed = load_missing_failed[failed_count_before:]
        if newly_failed:
            print(f"Failed this run: {newly_failed}")
            for el in newly_failed:
                if el in symbols:
                    symbols.remove(el)
        else:
            print("OK")
    values, counts = np.unique(load_missing_failed, return_counts=True)
    print(values, counts)

if __name__ == '__main__':
    ny_now = md.get_ny_now()
    nbus_days = get_nbusdays_from_date(ny_now)
    print('New York time now: {:%Y-%m-%d %H %A}'.format(ny_now), ' business days ago', nbus_days)
    # symbols = ['AAPL', 'MSFT','BW']
    incl = md.all
    symbols = md.get_symbols(incl)
    schedule = md.get_schedule()
    business_days = md.get_business_days(schedule)[1:]  # yesterday
    print('Starting business day ', business_days[0])
    run_mdb_missing(symbols, business_days)

