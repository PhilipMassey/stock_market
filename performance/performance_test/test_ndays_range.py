import market_data as md
import performance as pf

opt_ndays_range = pf.calc_percent_weekly
ndays_range = pf.get_ndays_range(opt_ndays_range)
print(ndays_range)