import market_data as md
import pandas as pd

def l_symbol_port_pos(symbol):
    dfs = ''
    directory = 'Seeking_Alpha'
    df_ports_syms = md.get_port_and_symbols(directory)
    sym_ports = df_ports_syms[df_ports_syms['symbol']==symbol].portfolio.values
    #s = pd.Series()
    s = []
    for port in sym_ports:
        port_symbols = md.get_symbols('',ports=[port])
        s.append((port,port_symbols.index(symbol)))
    return s

def df_symbol_sa_rating(symbol):
    ratings = l_symbol_port_pos(symbol)
    if len(ratings) == 0:
        return None
    else:
        s = ""
        ss = [s.join(rating[0][4:-6]+':'+str(rating[1])) for  rating in ratings]
        ratings_info = ', '.join(ss)
        ratings_sum = sum([(rating[1]) for  rating in ratings])
        ratings_len = len([(rating[1]) for  rating in ratings])
        ratings_grade = round(ratings_sum/ratings_len, 1)
        ndays = 1
        volume = md.get_mdb_value_column(ndays=1, column=symbol, coll_name=md.db_volume)
        return pd.DataFrame({'symbol': [symbol], 'ratings': ratings_info, 'length': [ratings_len], 'sum': [ratings_sum],
                             'grade': [ratings_grade], 'volume': [volume]})

def df_port_sa_rating(port):
    symbols = md.get_symbols('',ports=[port])
    dfall = pd.DataFrame()
    for symbol in symbols:
        df = df_symbol_sa_rating(symbol)
        if df is not None:
            dfall = pd.concat([dfall,df])
    return dfall


def df_directory_sa_rating(directory):
    if directory == 'Seeking_Alpha':
        ports = ['Top Stocks By Quant']
    else:
        ports = md.get_portfolios(directory)
    dfall = pd.DataFrame()
    for port in ports:
        df = df_port_sa_rating(port)
        #print(port,df)
        if df is not None:
            dfall = pd.concat([dfall,df])
    return dfall.drop_duplicates(subset = "symbol")



if __name__ == "__main__":
    directory = 'Seeking_Alpha'
    print(df_directory_sa_rating(directory))