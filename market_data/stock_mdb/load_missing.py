import market_data as md
import pandas as pd
from pymongo import MongoClient

client = MongoClient()
db = client['stock_market']


def update_mdb_with_missing_row(ndays, symbols, load_missing_failed):
    strdate = md.get_busdate_ndays_ago(ndays)
    print('ndays {} is the {}'.format(ndays,strdate), end=', ')
    df_m, dbaction, symbols = get_missing_market_row(ndays, symbols, load_missing_failed)
    if df_m.size > 0:
        print(int(df_m.size/2),dbaction)
        if dbaction == 'ADD':
            add_dfclosevol_row_to_dbs(df_m)
        elif dbaction == 'UPDATE':
            update_mdbs_row(df_m)
    return symbols

def get_missing_market_row(ndays, symbols, load_missing_failed):
    dbaction = None
    df_missing = pd.DataFrame({})
    missing_symbols = []
    df_mdb = md.get_df_from_mdb_for_nday(ndays, md.db_close, symbols)
    if df_mdb.size == 0: #missing whole row of data or missing symbols missing values 'Nan'
        count = md.mdb_document_count(ndays,md.db_close)
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
        print(dbaction, list(missing_symbols)[0:3], '....')
        df_missing = md.get_yahoo_ndays_ago(ndays, missing_symbols)
        df_missing = df_missing.dropna(axis=1, how='all')
        yahoo_symbols = df_missing['Close'].columns.values
        for el in missing_symbols:
            if el not in yahoo_symbols:
                load_missing_failed.append(el)
    return (df_missing,dbaction, symbols)


def add_dfclosevol_row_to_dbs(df):
    md.add_df_to_db(df['Close'], md.db_close)
#    md.add_df_to_db(df['Volume'], md.db_volume)

def update_mdbs_row(df):
    md.update_mdb_with_dfrow(df['Close'], md.db_close)
    #md.update_mdb_with_dfrow(df['Volume'], md.db_volume)
