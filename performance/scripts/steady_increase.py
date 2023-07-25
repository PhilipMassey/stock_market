import sys; sys.path.extend(['/Users/philipmassey/PycharmProjects/stock_market'])
sys.path.extend(['/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages'])
import performance as pf
import market_data as md

print('{} steady increase'.format(md.get_date_for_mdb(0)))
print(md.db_5days_up)
week = (5,1)
period_interval = week
count = 5
percent = 0
nstart = 0
df_5days_5up = pf.get_df_steady_increase(nstart,period_interval,count,percent=percent,incl=md.all)
symbols = sorted(df_5days_5up.symbol.unique())
print(', '.join(symbols))
md.add_dfup_to_db(df_5days_5up,md.db_5days_up)
df = df_5days_5up[['symbol','percent','volume']].groupby(['symbol']).sum().sort_values(by='percent',ascending=False)
#print(df)
df = md.get_df_symbol_portfolios(symbols).sort_values(by=['portfolio'])
#print(df[['portfolio','symbol']])

print(md.db_9days_up)
period_interval = (10,1)
count = 9
nstart = 0
df_9days_up = pf.get_df_steady_increase(nstart, period_interval, count, incl=md.all)
symbols = sorted(df_9days_up.symbol.unique())
print(', '.join(symbols))
md.add_dfup_to_db(df_9days_up, md.db_9days_up)
#print(df_9days_up[['symbol','percent','volume']].groupby(['symbol']).sum())
#print(md.get_df_symbol_portfolios(symbols).sort_values(by=['portfolio']))

print(md.db_5weeks_up)
weekly = (25,5)
period_interval = weekly
count = 5
nstart = 0
dfwkly = pf.get_df_steady_increase(nstart,period_interval,count,incl=md.all)
symbols = sorted(dfwkly.symbol.unique())
print(', '.join(symbols))
md.add_dfup_to_db(dfwkly,md.db_5weeks_up)
#print(dfwkly[['symbol','percent','volume']].groupby(['symbol']).sum().sort_values(by='percent',ascending=False))
#print(md.get_df_symbol_portfolios(symbols).sort_values(by=['portfolio']))

