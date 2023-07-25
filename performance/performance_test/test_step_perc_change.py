import performance as pf
import market_data as md

ndays_step=md.get_period_interval(10)
print(ndays_step)
dfall = pf.get_today_sym_port_perc_fltrd(ndays_step, incl=md.sa)
portfolio = 'Health Care-Pharmaceuticals Momentum'
df = dfall[dfall.portfolio == portfolio].copy(deep=True).sort_values(by=['date','symbol'])

print(df[df.symbol=='NOVN'].percent)