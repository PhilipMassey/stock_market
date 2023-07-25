import market_data as md
import apis
import performance as pf
import pandas as pd


def df_overall_performance(ndays_range,symbols):
    df_all = md.df_mdb_clossins_for_ndays_range(ndays_range, symbols)
    periods = len(df_all.index)
    df_over_pct = df_all.pct_change(periods=periods-1)*100
    df_vars = df_over_pct
    df_over_pct.dropna(inplace=True)
    df_vars = df_over_pct.T
    df_vars.columns = ['over_pc']
    df_period_pct = df_all.pct_change(periods=1)*100
    df_period_pct.dropna(inplace=True)
    df_period_pct.std()
    df_vars['pc_mean'] = df_period_pct.mean()
    df_vars['pc_std'] = df_period_pct.std()
    df_vars.reset_index(inplace=True)
    df_vars.rename(columns={'index':'symbol'},inplace=True)
    df_vars = df_vars.round(1)
    return df_vars


# def df_overall_performance(ndays_range,symbols):
#     df_all = md.df_mdb_clossins_for_ndays_range(ndays_range, symbols)
#     over_perc= ((df_all.iloc[-1] -df_all.iloc[0]) /df_all.iloc[0])
#     over_perc = (100*over_perc).round(2)
#     df_over_perf = pd.DataFrame({'symbol':over_perc.index,'perc':over_perc.values})
#     return df_over_perf


def df_perc_by_sector_industry(ndays_range ,symbols ):
    fields = ['sectorname','primaryname','symbol']
    df = apis.df_symbol_profile(symbols, fields)
    df.dropna(inplace=True)
    return df


def df_secind_sym_perf(ndays_range, symbols):
    df_over_perf = df_overall_performance(ndays_range,symbols)
    df_sector_ind = df_perc_by_sector_industry(ndays_range, symbols)
    #df.set_index('symbol', inplace=True)
    df_sector_ind.rename(columns={'sectorname':'sector','primaryname':'industry'},inplace=True)
    df_secind_sym_perf = df_sector_ind.merge(df_over_perf,on='symbol',how='outer')
    cols = ['sector', 'industry', 'symbol','over_pc','pc_mean','pc_std']
    return df_secind_sym_perf[cols].sort_values(by =['sector', 'industry', 'symbol'])