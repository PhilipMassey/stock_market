import pandas as pd
import yfinance as yf
import market_data as md
import sys

def get_yahoo_ndays_ago(ndays , symbols):
    from_date, to_date = md.get_fromdate_and_todate(ndays - 1)
    df = yf.download(tickers=symbols, interval="1d", start=from_date, end=to_date, group_by='column',
                 auto_adjust=True, prepost=True, threads=True)
    #df = df.dropna(axis=1, how='all')
    if df.size == 0:
        print('no results from yahoo')
        sys.exit(1)
    return df[['Close']]

