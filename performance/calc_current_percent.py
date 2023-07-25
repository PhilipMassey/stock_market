import market_data as md
import performance as pf
import pandas as pd
import yfinance as yf


def df_calc_symbol_perc(df_all, calc_percent, ndays_range):
    dates_index = [md.dateindex_as_ddmmm(dt) for dt in df_all.index.values[1:]]
    df_percents = pd.DataFrame({})
    for symbol in df_all.columns.values:
        closings = df_all[symbol].values
        alist = []
        for idx in range(1,closings.shape[0]):      #(ndays_range)):
            if calc_percent == pf.calc_interval_overall:
                perc = (closings[idx] - closings[0])/closings[0]
            elif calc_percent == pf.calc_interval_between:
                perc = (closings[idx] - closings[idx-1])/closings[idx-1]
            alist.append((100*perc).round(2))
        df = pd.DataFrame({symbol:alist}, index = dates_index)
        df_percents = pd.concat([df_percents,df],axis=1)
    return df_percents.T

def df_all_overall_perc(df_all, df_percents):
    perc= ((df_all.iloc[-1] -df_all.iloc[0]) /df_all.iloc[0])
    perc = (100*perc).round(2)
    dfoverall = pd.DataFrame({'Overall':perc})
    return pd.concat([df_percents,dfoverall],axis=1)


def df_closing_percent_change(ndays_range, calc_percent, symbols):
    df_all = md.df_mdb_clossins_for_ndays_range(ndays_range, symbols)
    df_percents = df_calc_symbol_perc(df_all, calc_percent, ndays_range)
    if calc_percent == pf.calc_interval_between:
        df_percents = df_all_overall_perc(df_all, df_percents)
    return df_percents.reset_index().rename(columns={'index':'symbol'})


def df_today_prevday_percent_change(symbols):
    ndays = 1
    df_yesterday = md.get_df_from_mdb_for_nday(ndays,md.db_close,symbols)
    df = yf.download(tickers = symbols, period ="1d", interval ="1d", group_by ='column', auto_adjust = True, prepost = False, threads = True)
    df_today = df['Close']
    df_all = pd.concat([df_yesterday,df_today])
    df_percents = pd.DataFrame({})
    for symbol in symbols:
        closings =  df_all[symbol].values
        alist = []
        perc = (closings[1] - closings[0])/closings[0]
        alist.append((100*perc).round(2))
        dates = [md.get_date_for_ndays(0)]
        df = pd.DataFrame({symbol:alist}, index = dates)
        df_percents = pd.concat([df_percents,df],axis=1)
    return df_percents.T  #.rename(index={'index':'symbol'})

def df_closing_percent_change_current(ndays_range, calc_percent, symbols):
    df_ndays_perc = df_closing_percent_change(ndays_range, calc_percent, symbols)
    if md.isit_weekend() is True:
        df_all = df_ndays_perc
    else:
        df_perc_today = df_today_prevday_percent_change(symbols)
        df_perc_today = df_perc_today.reset_index().rename(columns={'index': 'symbol'})
        df_all = pd.concat([df_ndays_perc, df_perc_today], axis=1)
    return df_all.T.drop_duplicates().T

