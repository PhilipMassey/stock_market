import sys; sys.path.extend(['/Users/philipmassey/PycharmProjects/stock_market'])
sys.path.extend(['/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages'])
import performance as pf
import plots as pl
import market_data as md


ndays_step=md.get_period_interval()  # defaults start to 2020/04/01
ndays_step=md.get_period_interval(20)
ndays_step=md.get_period_interval(10)
ndays_step=md.get_period_interval(5)

for bucket in [md.sa,md.watching,md.ark]:
    dfall = pf.get_today_sym_port_perc_fltrd(ndays_step, incl=bucket)
    title = bucket
    title = '{} days,{} step - {}'.format(ndays_step[0],ndays_step[1],title)
    df = pf.aggregateOnPortfolio(dfall)
    pl.plotPortPercPeriods(df,title,'bar','portfolio')

# dfall = pf.get_today_sym_port_perc_fltrd(ndays_step, directory=md.Watching)
# title = 'Watching up to results_date_value'
# title = '{} days,{} step - {}'.format(ndays_step[0],ndays_step[1],title)
# df = pf.aggregateOnPortfolio(dfall)
# pl.plotPortPercPeriods(df,title,'bar', 'portfolio')

#pl.plotSymPercPerdiod(dfall,title,'bubble')
ndays_step=md.get_period_interval(5)
dfall = pf.get_today_sym_port_perc_fltrd(ndays_step, incl=md.etf)
print(dfall.portfolio.unique())
for portfolio in dfall.portfolio.unique():
    print(portfolio)
    df = dfall[dfall.portfolio==portfolio].copy(deep=True)
    title = portfolio
    title = '{} days,{} step - {}'.format(ndays_step[0],ndays_step[1],title)
    pl.plotPortPercPeriods(df,title,'bar', 'symbol')
