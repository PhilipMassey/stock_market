import market_data as md
import pandas as pd
from market_data.stock_mdb.mongo_connection_manager import get_mongo_database

db = get_mongo_database('stock_market')


def update_mdb_with_missing_row(ndays, symbols, load_missing_failed):
    strdate = md.get_busdate_ndays_ago(ndays)
    print('ndays {} is the {}'.format(ndays,strdate), end=', ')
    df_m, dbaction, symbols = get_missing_market_row(ndays, symbols, load_missing_failed)
    if df_m.size > 0:
        print(int(df_m.size),dbaction, end=', ')
        if dbaction == 'ADD':
            md.add_row_to_mdb(df_m, md.db_close)
        elif dbaction == 'UPDATE':
            md.update_mdb_with_dfrow(df['Close'], md.db_close)
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
        print(ndays,dbaction, list(missing_symbols)[0:3], '....')
        df_missing = md.get_yahoo_ndays_ago(ndays, missing_symbols)
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
            
    return (df_missing,dbaction, symbols)

