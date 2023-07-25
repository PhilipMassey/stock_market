import pandas as pd

import market_data as md
import performance as pf
import pandas as pd

def df_monthly_option(perc_or_mean, directory, port):
    ndays_periods = md.get_ndays_range_montlhly(end=1)
    results_date_value = md.get_date_for_ndays(ndays_periods[0])
    df = pd.DataFrame({})
    if perc_or_mean == pf.perc_option:
        if directory != None and port == None:
            symbols = md.get_symbols(directory=directory)
            df = pf.df_percents_between_days(ndays_periods, symbols=symbols, db_coll_name=md.db_close)
        elif directory != None and port != None:
            symbols = md.get_symbols(ports=[port])
            df = pf.df_percents_between_days(ndays_periods, symbols=symbols, db_coll_name=md.db_close)
        else:
            df = pf.df_percents_between_days(ndays_periods)
    elif perc_or_mean == pf.mean_option:
        df = pf.df_dir_ports_means_between_days(ndays_periods, directory)
    return (results_date_value, df)


def df_wfm3612_option(perc_or_mean, directory, port):
    ndays_range = md.get_ndays_range_wfm3612(end=1)
    results_date_value = md.get_date_for_ndays(ndays_range[-1])
    df = pd.DataFrame({})
    if perc_or_mean == pf.perc_option:
        if directory != None and port == None:
            symbols = md.get_symbols(directory=directory)
            df = pf.df_percents_for_range(ndays_range, symbols=symbols)
        elif directory != None and port != None:
            symbols = md.get_symbols(ports=[port])
            df = pf.df_percents_for_range(ndays_range, symbols=symbols)
        else:
            df = pf.df_percents_for_range(ndays_range)
    elif perc_or_mean == pf.mean_option:
        df = pf.df_dir_ports_means_for_range(ndays_range, directory)
    return (results_date_value, df)
