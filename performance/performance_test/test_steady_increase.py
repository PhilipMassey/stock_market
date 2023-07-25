import performance as pf
import market_data as md

week = (5,1)
period_interval = week
count = 5
nstart = 1
dfwk5 = pf.get_df_steady_increase(nstart,period_interval,count,incl=md.all)

print(dfwk5)