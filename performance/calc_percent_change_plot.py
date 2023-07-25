import market_data as md
import performance as pf
import pandas as pd


def df_calc_symbol_perc_plot(df_all, calc_percent, ndays_range):
    dates_index = [dt for dt in df_all.index.values[1:]]
    df_percents = pd.DataFrame({})
    for symbol in df_all.columns.values:
        closings =  df_all[symbol].values
        alist = []
        for idx in range(1,closings.shape[0]):  #len(ndays_range)):
            if calc_percent == pf.calc_interval_overall:
                perc = (closings[idx] - closings[0])/closings[0]
            elif calc_percent == pf.calc_interval_between:
                perc = (closings[idx] - closings[idx-1])/closings[idx-1]
            alist.append((100*perc).round(2))
        df = pd.DataFrame({symbol:alist}, index = dates_index)
        df_percents = pd.concat([df_percents,df],axis=1)
    return df_percents.T


def df_calc_percent_change_zero(ndays_range, calc_percent,symbols):
    #calc_percent = pf.calc_interval_overall
    df_all = md.df_mdb_clossins_for_ndays_range(ndays_range, symbols)
    dfperc = df_calc_symbol_perc_plot(df_all, calc_percent, ndays_range)
    dfperc = dfperc.T
    dfperc.index.rename('Date',inplace=True)
    df0 = pd.DataFrame({df_all.index.values[0]:0},df_all.columns )
    df0 = df0.T
    df0.index.rename('Date',inplace=True)
    df = pd.concat([df0,dfperc])
    return df