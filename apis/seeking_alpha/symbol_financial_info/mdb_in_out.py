import pandas as pd
from bson import json_util
from pandas import json_normalize
import json
# Use shared connection manager
from market_data.stock_mdb.mongo_connection_manager import get_mongo_database

# Default to stock_market DB to avoid importing market_data at top level
db = get_mongo_database('stock_market')



def df_symbol_profile(symbols=[],fields=None) -> list:
    import market_data as md
    coll_name = md.db_symbol_profile
    db_coll = db[coll_name]
    if len(symbols) == 0:
        mongo_data = db_coll.find({},fields)
    else:
        mongo_data = db_coll.find({"symbol": {"$in": symbols}},fields)
    sanitized = json.loads(json_util.dumps(mongo_data))
    df = json_normalize(sanitized)
    df.drop(columns=['_id.$oid'],inplace=True)
    return df


def dct_mdb_symbol_fields(symbols=[],fields=None) -> dict:
    df = df_symbol_profile(symbols, fields)
    df.set_index('symbol',inplace=True)
    return pd.DataFrame.to_dict(df)


def dct_mdb_symbol_names(symbols=[]) -> dict:
    fields = ['symbol','companyName']
    dct = dct_mdb_symbol_fields(symbols,fields)
    return dct["companyName"]


def dct_mdb_symbol_industry_sector(symbols=[]) -> dict:
    fields = ['symbol','sectorname','primaryname']
    dct = dct_mdb_symbol_fields(symbols,fields)
    return dct['sectorname'],dct['primaryname']


def get_sectors_industry():
    import market_data as md
    coll_name = md.db_symbol_profile
    db_coll = db[coll_name]
    mongo_data = db_coll.find()
    sanitized = json.loads(json_util.dumps(mongo_data))
    df = json_normalize(sanitized)
    df.drop(columns=['_id.$oid'],inplace=True)
    df = df[['sectorname', 'primaryname']].dropna()
    df.rename(columns={'sectorname': 'sector', 'primaryname': 'industry'}, inplace=True)
    return df