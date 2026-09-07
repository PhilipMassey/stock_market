# import sys
#
# # Add the project root to the Python path
# sys.path.append("/Users/philipmassey/stock_market")

import market_data as md
import performance as pf
import pandas as pd
import datetime

global_cache = {
    'date': None,
    'df_all_periods': None
}


def get_all_periods_ranked():
    import scipy.stats as stats
    today = datetime.datetime.now().strftime('%Y-%m-%d %H')  # Cache per hour
    if global_cache['date'] == today and global_cache['df_all_periods'] is not None:
        return global_cache['df_all_periods']

    symbols = md.get_symbols(md.all)
    all_dfs = []
    periods = [
        ('Daily', pf.calc_percent_daily),
        ('1 Week', pf.calc_percent_weekly),
        ('2 Weeks', pf.calc_percent_2weekly),
        ('1 Month', pf.calc_percent_monthly),
        ('2 Months', pf.calc_percent_2monthly)
    ]

    for period_name, opt_val in periods:
        ndays_range = pf.get_ndays_range(opt_val)
        df_all = pf.df_secind_sym_perf(ndays_range, symbols)

        ind_mean_pc = df_all.groupby(['sector', 'industry'])['over_pc'].transform('mean')
        df_all['rel_strength_ind'] = df_all['over_pc'] - ind_mean_pc

        mask_std_gt_0 = df_all['pc_std'] > 0
        df_all['prob_green_day_%'] = 0.0
        df_all.loc[mask_std_gt_0, 'prob_green_day_%'] = stats.norm.sf(0, loc=df_all.loc[mask_std_gt_0, 'pc_mean'],
                                                                      scale=df_all.loc[mask_std_gt_0, 'pc_std']) * 100

        df_all['stretch_score'] = 0.0
        df_all.loc[mask_std_gt_0, 'stretch_score'] = df_all.loc[mask_std_gt_0, 'over_pc'] / df_all.loc[
            mask_std_gt_0, 'pc_std']

        df_all['kelly_fraction'] = 0.0
        df_all.loc[mask_std_gt_0, 'kelly_fraction'] = df_all.loc[mask_std_gt_0, 'pc_mean'] / (
                    df_all.loc[mask_std_gt_0, 'pc_std'] ** 2)

        df_all['risk_reward_rank'] = df_all['risk_reward'].rank(ascending=False, method='min')
        df_all['rel_strength_ind_rank'] = df_all['rel_strength_ind'].rank(ascending=False, method='min')
        df_all['prob_green_day_rank'] = df_all['prob_green_day_%'].rank(ascending=False, method='min')
        df_all['stretch_score_rank'] = df_all['stretch_score'].rank(ascending=False, method='min')
        df_all['kelly_fraction_rank'] = df_all['kelly_fraction'].rank(ascending=False, method='min')

        df_all['Period'] = period_name
        date_newest = md.get_date_for_ndays(ndays_range[-1])
        date_oldest = md.get_date_for_ndays(ndays_range[0])
        df_all['Date Range'] = f"{date_oldest} to {date_newest}"

        all_dfs.append(df_all)

    df_concat = pd.concat(all_dfs, ignore_index=True)
    global_cache['date'] = today
    global_cache['df_all_periods'] = df_concat
    return df_concat


# Sectors logic
if hasattr(md, 'df_sector_ind'):
    df_sector_ind = md.df_sector_ind
elif hasattr(md, 'get_sector_data'):
    df_sector_ind = md.get_sector_data()
else:
    df_sector_ind = pd.DataFrame()

if not df_sector_ind.empty and 'sector' in df_sector_ind.columns:
    sectors = sorted(list(df_sector_ind['sector'].unique()))
else:
    sectors = []

df_all = get_all_periods_ranked()
print(df_all)