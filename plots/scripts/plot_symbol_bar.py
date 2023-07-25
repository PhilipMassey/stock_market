import performance as pf
import plots as pl
import market_data as md


ndays_step=md.get_period_interval()  # defaults start to 2020/04/01
ndays_step=md.get_period_interval(30)
print(ndays_step)

portfolio = md.sa
dfall = pf.get_today_sym_port_perc_fltrd(ndays_step, incl=portfolio)
portfolio = 'Health Care-Pharmaceuticals Momentum'

portfolio
df = dfall[dfall.portfolio == portfolio].copy(deep=True).sort_values(by=['date','symbol'])
title = '{} days,{} step - {}'.format(ndays_step[0],ndays_step[1],portfolio)
pl.plotPortPercPeriods(df,title,'bar','symbol')
