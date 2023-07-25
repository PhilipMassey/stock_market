import requests
import pandas as pd
import market_data as md
import apis
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from bson import json_util
from pandas import json_normalize
import json

client = MongoClient()
db = client['stock_market']


key_data_fields = ['eps','peRatioFwd','estimateEps','divYield','marketCap','volume','evEbit','evEbitda','evFcf','evSales','fcf','fcfShare','marketCap','movAvg10d','movAvg10w','movAvg200d','payout4y','payoutRatio','pegRatio','peRatioFwd','priceBook','priceCf','priceSales','priceTangb','quickRatio','revenueGrowth','revenueGrowth3','revPShare','revToAssets','roa','roe','shares','ltDebtCap']

key_data_url = "https://seeking-alpha.p.rapidapi.com/symbols/get-key-data"
key_data_headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': md.seeking_alpha_key
    }


def df_symbol_key_data(symbol,key_data_fields):
    symbol = symbol.upper()
    querystring = {'symbol':symbol}
    response = requests.request("GET", key_data_url, headers=key_data_headers, params=querystring)
    symbol_dct = response.json()['data'][0]
    dct_attribs =symbol_dct['attributes']
    symbol_fields ={}
    keys = dct_attribs.keys()
    for field in key_data_fields:
        if field in keys:
            symbol_fields[field] = dct_attribs[field]
    df = pd.DataFrame.from_dict(symbol_fields, orient='index',columns=[symbol] )
    df = df.T.reset_index().rename(columns={'index':'symbol'})
    return df

summary_fields = ['shortIntPctFloat','peRatioFwd','estimateEps','divYield','marketCap','volume','evEbit','evEbitda','evFcf','evSales','fcf','fcfShare','marketCap','movAvg10d','movAvg10w','movAvg200d','payout4y','payoutRatio','pegRatio','peRatioFwd','priceBook','priceCf','priceSales','priceTangb','quickRatio','revenueGrowth','revenueGrowth3','revPShare','revToAssets','roa','roe','shares','ltDebtCap']

summary_url = "https://seeking-alpha.p.rapidapi.com/symbols/get-summary"

summary_headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key':  md.seeking_alpha_key
    }

def df_symbol_summary_fields(symbol,summary_fields):
    symbol = symbol.upper()
    querystring = {'symbols':symbol}
    response = requests.request("GET", summary_url, headers=summary_headers, params=querystring)
    dctall = response.json()['data']
    for idx in range(len(dctall)):
        symbol_dct = dctall[idx]
        symbol_info = {}
        #symbol = symbol_dct['id']
        dct_attribs =symbol_dct['attributes']
        keys = dct_attribs.keys()
        symbol_fields ={}
        for field in summary_fields:
            if field in keys:
                symbol_fields[field] = dct_attribs[field]
        df = pd.DataFrame.from_dict(symbol_fields, orient='index',columns=[symbol] )
        df = df.T.reset_index().rename(columns={'index':'symbol'})
        return df

def df_symbol_info(ndays, symbol):
    symbol = symbol.upper()
    dfs = apis.df_symbol_summary_fields(symbol, summary_fields)
    dfk = apis.df_symbol_key_data(symbol, key_data_fields)
    df = pd.concat([dfs, dfk], axis=1)
    df = df.T.drop_duplicates().T
    md.df_add_date_index(ndays, df)
    return df


def count_mdb_symbol_detween_dates(ndays,period,symbol,db_coll_name):
    symbol = symbol.upper()
    start_date, end_date = md.get_ndate_and_todate(ndays,period)
    start_date, end_date = md.get_mdbdate_from_strdate(start_date),md.get_mdbdate_from_strdate(end_date)
    db_coll = db[db_coll_name]
    return db_coll.count_documents({'Date': {'$lte':end_date, '$gte':start_date}, 'symbol':symbol})

def add_symbol_info_mdb(ndays,period, symbol,df , db_coll_name):
    symbol = symbol.upper()
    count = 0
    try:
        count = count_mdb_symbol_detween_dates(ndays, period, symbol, db_coll_name)
        if count == 0:
            results = md.add_df_to_db(df, db_coll_name, dropidx=False)
            #print(len(results.inserted_ids))
            count = len(results.inserted_ids)
    except BulkWriteError as bwe:
        print("Duplicate entry" ,df.index.values[0],df.symbol.values[0])
    return count
