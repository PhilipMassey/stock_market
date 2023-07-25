from datetime import datetime, timedelta
import calendar

import pandas as pd
import yfinance as yf
import plotly.express as px


def getSymbolsSecInd(symbols):
    market_data_dir = '/Users/philipmassey/PycharmProjects/stock_market/market_data'
    df_secind = pd.read_pickle(market_data_dir+'/name_sector_industry.pkl')
    df_secind = df_secind.set_index('name')
    df_secind = df_secind.sort_index()
    secinds = set(df_secind.index.values)
    diff = secinds - symbols
    return df_secind.drop(diff)


