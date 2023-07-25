import market_data as md
import apis
def df_mdb_symbol_profile(symbol,fields=''):
    db_coll_name = md.db_symbol_profile
    ndays = 0
    period = 1000
    symbols = [symbol]
    df = md.df_mdb_between_days(ndays, period, symbols, db_coll_name, fields)
    df.index = df.index.strftime('%m/%d/%Y')
    df = df.T
    df.reset_index(inplace=True)
    df = df.rename(columns={'index': 'Date'})
    return df

def df_mdb_symbol_info(symbol,fields=''):
    db_coll_name = md.db_symbol_info
    ndays = 0
    period = 1000
    symbols = [symbol]
    df = md.df_mdb_between_days(ndays, period, symbols, db_coll_name, fields)
    df.index = df.index.strftime('%m/%d/%Y')
    df = df.T
    df.reset_index(inplace=True)
    df = df.rename(columns={'index': 'Date'})
    return df
