import pandas as pd
import yfinance as yf
import market_data as md
import sys

def get_yahoo_ndays_ago(ndays, symbols):
    if 'Date' in symbols:
        symbols.remove('Date')
    if len(symbols) == 1:
        symbols = list(symbols)
        symbols.append('SPY')
    if len(symbols) == 0:
        df = pd.DataFrame({})
    elif ndays == 0:
        df = yf.download(tickers=symbols, period="1d", interval="1d", group_by='column', auto_adjust=True,
                         prepost=True, threads=True)
    elif ndays == 1:
        df = yf.download(tickers=symbols, period="2d", interval="1d", group_by='column', auto_adjust=False,
                         prepost=True, threads=True)
    else:
        #start, end = md.get_dates_ndays_and_today(ndays)
        start, end = md.get_ndate_and_prevdate(ndays - 1)
        df = yf.download(tickers=symbols, interval="1d", start=start, end=end, group_by='column',
                         auto_adjust=True, prepost=True, threads=True)
        #df.drop('SPY', axis=1, level=1, inplace=True, errors='ignore')
        df = df.dropna(axis=1, how='all')
    pddate = md.get_pd_time_series_for_ndays(ndays)
    if pddate in df.index:
        df = df.loc[[pddate]]
    else:
        df = pd.DataFrame({})
    #df.drop('SPY', axis=1, level=1, inplace=True, errors='ignore')
    df = df.dropna(axis=1, how='all')
    if df.size == 0:
        print('no results from yahoo')
        sys.exit(1)
    # if len(df['Close'].columns) < len(symbols):
    #     failed = set(symbols).difference(df['Close'].columns)
    #     print('yahoo failed to download:', failed)
    #     md.load_missing_failed + list(failed)
    if df.size == 0:
        return pd.DataFrame({})
    else:
        return df[['Close', 'Volume']]

def get_yahoo_ndays_plus(ndays, interval, symbols):
    if 'Date' in symbols:
        symbols.remove('Date')
    if len(symbols) == 0:
        df = pd.DataFrame({})
    start, end = md.get_ndate_and_todate(ndays-1, interval)
    df = yf.download(tickers=symbols, interval="1d", start=start, end=end, group_by='column',
                         auto_adjust=True, prepost=True, threads=True)
        #df.drop('FB', axis=1, level=1, inplace=True, errors='ignore')
    df = df.dropna(axis=1, how='all')
    strdate = md.get_mdb_strdate_for_ndays(ndays)
    df = df.dropna(axis=1, how='all')
    if df.size == 0:
        return pd.DataFrame({})
    else:
        return df[['Close', 'Volume']]
