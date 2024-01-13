import pandas as pd
import market_data as md
from os.path import isfile, join, isdir
from os import listdir


def get_portfolio_dirs():
    return sorted(d for d in listdir(md.data_dir) if isdir(join(md.data_dir, d)))


def add_portfolio_to_df_stock(df_stock, incl):
    df_stock = df_stock.reset_index().rename(columns=({'index': 'symbol'}))
    df_port = md.get_port_and_symbols(incl)
    return df_stock.merge(df_port)


def get_df_symbol_portfolios(symbols):
    df = pd.DataFrame({})
    df['symbol'] = symbols
    df_port = md.get_port_and_symbols(directories=md.all)
    return df.merge(df_port).sort_values(by=['portfolio'])


def index_to_column(df, column):
    df = df.reset_index().rename(columns=({'index':column}))
    return df.sort_values(by=[column])


def get_md_port_mangle():
    portfolios = sorted(md.get_portfolios(directory=md.all))
    for op in portfolios:
        p = op.lower()
        p = p.replace(' ', '_')
        p = p.replace('-', '_')
        print(f"{p} = '{op}'")