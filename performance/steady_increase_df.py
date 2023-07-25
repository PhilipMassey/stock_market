import pandas as pd
import market_data as md
import performance as pf

def get_df_steady_increase(nstart, period_interval, count, percent=0, incl=md.all):
    dfall = pf.getPrevDaySymPortPercPeriods(nstart, period_interval, incl)
    dfall = dfall.drop(['index', 'portfolio'], axis=1)
    dfall = dfall.drop_duplicates()
    df = dfall
    df = df[df.percent >= percent].dropna().groupby(['symbol']).count().sort_values(by=['percent']).rename(
        columns={'percent': 'count'})[['count']]
    dfn = df[df['count'] >= count]
    dfn.reset_index(drop=False, inplace=True)
    return dfall[dfall.symbol.isin(dfn['symbol'].values)].sort_values(by=['symbol'], ascending='False')


def get_symbols_steady_increase(nstart, period_interval, count):
    df = get_df_steady_increase(nstart, period_interval, count)
    return ', '.join(pd.unique(df.symbol))
