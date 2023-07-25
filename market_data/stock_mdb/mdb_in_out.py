import market_data as md
import performance as pf
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from bson import json_util
from pandas import json_normalize
import json

client = MongoClient()
db = client['stock_market']

def mdb_add_df(df,db_coll_name):
    data_dict = df.to_dict("records")
    db_coll = db[db_coll_name]
    result = db_coll.insert_many(data_dict)
    return len(result.inserted_ids  )


def add_df_to_db(df, db_coll_name, dropidx=False):
    db_coll = db[db_coll_name]
    df = df.copy(deep=True)
    df.drop_duplicates(inplace=True)
    df.reset_index(inplace=True)
    if dropidx == True:
        df.drop(columns={'index'},inplace=True)
    data_dict = df.to_dict("records")
    #print(data_dict)
    result = db_coll.insert_many(data_dict)
    #print('Inserted {:d} into {}' .format(len(result.inserted_ids),db_coll_name))   #,len(df.index)))
    return result




def add_dct_to_mdb(dct, db_coll_name):
    db_coll = db[db_coll_name]
    df = pd.DataFrame.from_dict(dct)
    data = df.to_dict('records')
    result = db_coll.insert_many(data)
    return result

def update_mdb_with_dfrow(df_m, coll_name):
    db_coll = db[coll_name]
    dt = md.df_idxdate_to_mdbdate(df_m)
    #print('update_mdb', df_m)
    if df_m.size > 0:
        df_mc = df_m.copy(deep=True)
        df_mc = df_mc.dropna(axis='columns')
        df_mc.reset_index(inplace=True)
        df_mc.drop(columns=['Date'], inplace=True)
        data_dict = df_mc.to_dict("records")
        # print(data_dict)
        newvalues = {"$set": data_dict[0]}
        query = {'Date': dt}
        result = db_coll.update_one(query, newvalues)
        #print(ndays, len(data_dict[0]), result.matched_count, result.modified_count)

def update_mdb_with_dfrows(df,db_coll_name):
    for index, row in df.iterrows():
        dfrow = pd.DataFrame({index:row}).T.rename_axis('Date')
        md.update_mdb_with_dfrow(dfrow, md.db_test_close)


def add_dfup_to_db(dfup, db_coll_name):
    dt = max(dfup.date.values)
    dt = md.get_mdbdate_from_strdate(dt)
    df = pd.DataFrame(columns=['Date', 'symbol'])
    df['symbol'] = dfup.symbol.unique()
    df['Date'] = dt
    md.add_df_to_db(df, db_coll_name, dropidx=True)


def get_mdb_rows_close_vol(strdate, incl=md.all):
    adate = get_mdbdate_from_strdate(strdate)
    dbcoll_name = md.db_close
    dfClose = md.get_mdb_row_for_date(adate, dbcoll_name,addtodb=True)
    dbcoll_name = md.db_volume
    dfVol = md.get_mdb_row_for_date(adate, dbcoll_name,addtodb=True)
    if incl != md.all:
        dfClose = pf.filteredbySymbols(dfClose, incl, colorrow='col')
        dfVol = pf.filteredbySymbols(dfVol, incl, colorrow='col')
    return dfClose,dfVol


def mdb_to_df(mongo_data, dateidx=False):
    sanitized = json.loads(json_util.dumps(mongo_data))
    normalized = json_normalize(sanitized)
    df = pd.DataFrame(normalized)
    if dateidx == True:
        replace_date_date(df)
    return df


def replace_date_date(df):
    #df['Date'] = datetime.utcfromtimestamp(float(df['Date.$date'] / 1e3))
    df['Date'] = df['Date.$date'].apply(lambda x: datetime.utcfromtimestamp(float(x / 1e3)))
    df.set_index('Date', inplace=True)
    df.drop(['Date.$date', '_id.$oid'], axis=1, inplace=True)


def display_index(db_coll_name):
    df = md.get_df_from_mdb_columns([],db_coll_name)
    print(set(df.index))

def count_mdb_on_date(ndays,symbol,db_coll_name):
    symbol = symbol.upper()
    adate = md.get_date_for_mdb(ndays)
    db_coll = db[db_coll_name]
    return db_coll.count_documents({'Date': adate, 'symbol':symbol})


def df_from_mdb_all_data(db_coll_name, columns=[]):
    db_coll = db[db_coll_name]
    if len(columns) != 0:
        columns.append('Date')
        mdb_data= db_coll.find({}, columns)
    else:
        mdb_data= db_coll.find({})
    return md.mdb_to_df(mdb_data, dateidx=True)


def df_from_mdb_filter(db_coll_name, afilter, columns=[]):
    db_coll = db[db_coll_name]
    if len(columns) != 0:
        columns.append('Date')
        mdb_data= db_coll.find({'symbol':afilter}, columns)
    else:
       mdb_data= db_coll.find({'symbol':afilter})
    return md.mdb_to_df(mdb_data, dateidx=True)

def get_mdb_value_column(ndays, column, coll_name):
    value = 0
    adate = md.get_date_for_mdb(ndays)
    db_coll = db[coll_name]
    if db_coll.count_documents({'Date': adate}) > 0:
        mdb_data = db_coll.find({'Date': adate},{column:1})
        sanitized = json.loads(json_util.dumps(mdb_data))
        normalized = json_normalize(sanitized)
        value = normalized[column][0]
    return value

