import market_data as md
import pandas as pd
from datetime import datetime

from bson import json_util
from pandas import json_normalize
import json

from pymongo import MongoClient
client = MongoClient()
db = client[md.db_client]

def get_df_from_mdb_for_nday(ndays, coll_name, symbols='', incl='', dateidx=True):
    db_coll = db[coll_name]
    adate = md.get_date_for_mdb(ndays)
    df = pd.DataFrame({})
    if len(incl) != 0:
        symbols = md.get_symbols(incl)
    if db_coll.count_documents({'Date': adate}) > 0:
        if len(symbols) > 0:
            symbols.append('Date')  # Date field to be included in mdb results
            mdb_data = db_coll.find({'Date': adate},symbols)
            symbols.remove('Date')
        else:
            mdb_data = db_coll.find({'Date': adate})
        df = md.mdb_to_df(mdb_data, dateidx)
    #print('mdb records {} for {} symbols on {}'.format(df.size,len(symbols),adate),end=', ')
    return df


# def get_df_from_mdb(db_coll_name,columns=''):
#     db_coll = db[db_coll_name]
#     if len(columns) == 0:
#         mdb_data = db_coll.find()
#     else:
#         mdb_data = db_coll.find(columns)
#     df = md.mdb_to_df(mdb_data)
#     return df


def df_mdb_clossins_for_ndays_range(ndays_range, symbols):
    df_all = pd.DataFrame({})
    for ndays in ndays_range:
            df = get_df_from_mdb_for_nday(ndays,md.db_close,symbols)
            df_all = pd.concat([df_all,df])
    return df_all


def get_df_from_mdb_between_days(ndays_ago, dbcol_name, symbols='', incl=md.all, last_day=1):
    db_coll = db[dbcol_name]
    start_date = md.get_date_for_mdb(ndays_ago)
    if not 'Date' in symbols:
        symbols.append('Date')
    df = pd.DataFrame({})
    if last_day==1:     #last instert
        mdb_data = db_coll.find({'Date': {'$gte':start_date}},symbols)
    else:
        end_date = md.get_date_for_mdb(start)
        mdb_data = db_coll.find({'Date': {'$lte':end_date, '$gte':start_date}},symbols)
    df = md.mdb_to_df(mdb_data, dateidx=True)
    return df


### SYMBOL queries

def get_df_from_mdb_columns(columns, dbcol_name):
    columns.append('Date')
    db_coll = db[dbcol_name]
    mdb_data= db_coll.find({}, columns)
    df = md.mdb_to_df(mdb_data, dateidx=True)
    return df


## REDUNDANT


def get_df_mdb_nrows_step(start,days_step, coll_name,symbols='', incl=md.all):
    days,step = days_step[0],days_step[1]
    dfa = pd.DataFrame(columns=['Date'])
    for ndays in range(start,start+days,step):
        df = get_df_from_mdb_for_nday(ndays, coll_name, symbols)
        df = df.reset_index().rename(columns={'index':'Date'})
        dfa = pd.concat([dfa,df])
    dfa.sort_values(by=['Date'], ascending=[True], inplace=True)
    return dfa


def mdb_document_count(ndays, db_coll_name):
    adate = md.get_date_for_mdb(ndays)
    db_coll = db[db_coll_name]
    return db_coll.count_documents({'Date': adate})


def mdb_profile_get_symbols(symbols=[]) -> list:
    coll_name = md.db_symbol_profile
    db_coll = db[coll_name]
    if len(symbols) == 0:
        mongo_data = db_coll.find()
    else:
        mongo_data = db_coll.find({"symbol": {"$in": symbols}})
    sanitized = json.loads(json_util.dumps(mongo_data))
    df = json_normalize(sanitized)
    return list(df.symbol.values)

def df_mdb_between_days(ndays, period, symbols, db_coll_name,fields=None):
    start_date, end_date = md.get_ndate_and_todate(ndays,period)
    start_date, end_date = md.get_mdbdate_from_strdate(start_date),md.get_mdbdate_from_strdate(end_date)
    db_coll = db[db_coll_name]
    if not 'Date' in symbols:
        symbols.append('Date')
    mdb_data = db_coll.find({'Date': {'$lte':end_date, '$gte':start_date}, 'symbol': {'$in' : symbols}},fields)
    df = md.mdb_to_df(mdb_data, dateidx=True)
    return df
