import nbformat as nbf
import os

# Define common setup code for the start of the notebook
setup_code_1 = """\
import gspread
from gspread_dataframe import get_as_dataframe

# Authenticate with your Google account
gc = gspread.service_account(filename='/Users/philipmassey/.config/gspread/service_account.json')

import sys
import os
import pandas as pd
import numpy as np

# Add the parent directory to the path so we can import the project modules
sys.path.append(os.path.abspath('../../'))

import market_data as md
import performance as pf

dct_workbook_url = {
    'Portfolio Adjustments': 'https://docs.google.com/spreadsheets/d/1bTsH3cjQDGR-Mlnq-bypRqhGIHJApKKJgsgXWSemur4/edit#gid=0',
    'Dividends': 'https://docs.google.com/spreadsheets/d/1N1zyOStCH-gvYAgCnv6vtmsTkp6q7R8rpAnzwv9W1sI/edit?gid=0',
    'Relative Strength / Sector Leadership': 'https://docs.google.com/spreadsheets/d/16f_asTlYBbUpq9dkoV3Wqvc1wc71YVI4MbO7LUf7dpI/edit?gid=0',
    'Quality Of Trend Consistency': 'https://docs.google.com/spreadsheets/d/1DE95ydBHX1J5LrvuuHN3_wy1iCzYbtjfpJR28mcQwnk',
    'Probability Of Positive Day': 'https://docs.google.com/spreadsheets/d/1oSyGUY7aiBcjWlKYa5EvXFrmOUpWlasLmT94RSIeRjU',
    'Mean Reversion Rubber Band': 'https://docs.google.com/spreadsheets/d/188r11UEo0rrh-uZT-4mz1pnQj__rBOp1XyN5FuOzMRc',
    'Kelly Criterion Optimal Sizing': 'https://docs.google.com/spreadsheets/d/1rIeckdcAxFiqJDuEaClYL0uahnDddxDtEPAyyIZM1Cs'
}

dct_worksheet_ids = {
    'Relative Strength / Sector Leadership': {pf.calc_percent_daily:0, pf.calc_percent_weekly:1171511640, pf.calc_percent_2weekly:1906167718, pf.calc_percent_monthly:2087427134, pf.calc_percent_2monthly:396380362},
    'Quality Of Trend Consistency': {pf.calc_percent_daily: 0, pf.calc_percent_weekly: 368623089, pf.calc_percent_2weekly: 31392050, pf.calc_percent_monthly: 1948826216, pf.calc_percent_2monthly: 1625076267},
    'Probability Of Positive Day': {pf.calc_percent_daily: 0, pf.calc_percent_weekly: 911684053, pf.calc_percent_2weekly: 2001663835, pf.calc_percent_monthly: 707711513, pf.calc_percent_2monthly: 1808101499},
    'Mean Reversion Rubber Band': {pf.calc_percent_daily: 0, pf.calc_percent_weekly: 1645850023, pf.calc_percent_2weekly: 2020910653, pf.calc_percent_monthly: 550915282, pf.calc_percent_2monthly: 1119783595},
    'Kelly Criterion Optimal Sizing': {pf.calc_percent_daily: 0, pf.calc_percent_weekly: 891321177, pf.calc_percent_2weekly: 1723754803, pf.calc_percent_monthly: 1285903326, pf.calc_percent_2monthly: 1948635551}
}

def worksheet_update_with_df(workbook_name, worksheet_id, df):
    workbook_url = dct_workbook_url[workbook_name]
    workbook = gc.open_by_url(workbook_url)
    worksheet = workbook.get_worksheet_by_id(worksheet_id)
    # If you need to clear old data that might be longer than the new DataFrame,
    # use batch_clear() with a range. This clears VALUES but keeps FORMATTING.
    worksheet.batch_clear(["A1:Z500"])
    # Use set_with_dataframe to update values only.
    # It preserves existing formatting (colors, fonts, borders).
    result = md.set_with_dataframe(worksheet, df, row=1, col=1, include_index=False, include_column_header=True)
    print('\\tupdated', worksheet.title, '\\t',result)
"""

loop_code_start = """\

# Get Data using the daily timeframe (same as the percent_mean_std page)
for opt_ndays_range in [pf.calc_percent_daily, pf.calc_percent_weekly, pf.calc_percent_2weekly, pf.calc_percent_monthly, pf.calc_percent_2monthly]:    
    ndays_range = pf.get_ndays_range(opt_ndays_range)
    worksheet_id = dct_worksheet_ids[workbook_name][opt_ndays_range]
    print(f"\\nProcessing timeframe: {ndays_range} (worksheet ID: {worksheet_id})")
    
    symbols = md.get_symbols(md.all)
    # Fetch the core dataframe
    df_raw = pf.df_secind_sym_perf(ndays_range, symbols)
    df = df_raw.dropna(subset=['over_pc', 'pc_mean', 'pc_std']).copy()
"""

# ==========================================
# Notebook 1: Relative Strength
# ==========================================
nb1 = nbf.v4.new_notebook()
nb1['cells'] = [
    nbf.v4.new_markdown_cell("# Relative Strength / Sector Leadership\nThis notebook evaluates \"Alpha\". It calculates the average performance (`over_pc`) for the entire industry and sector. It then isolates stocks that are vastly outperforming their industry average (Sector Leaders) with high `risk_reward` metrics."),
    nbf.v4.new_code_cell(setup_code_1),
    nbf.v4.new_code_cell(f"""\
workbook_name = 'Relative Strength / Sector Leadership'
{loop_code_start}
    # Calculate Industry and Sector averages for overall performance
    industry_means = df.groupby(['sector', 'industry'])['over_pc'].transform('mean')
    sector_means = df.groupby('sector')['over_pc'].transform('mean')
    
    df['ind_mean_pc'] = industry_means
    df['sec_mean_pc'] = sector_means
    
    # Calculate relative strength against their industry
    df['rel_strength_ind'] = df['over_pc'] - df['ind_mean_pc']
    
    # Filter for the "Sector Leaders"
    # These are stocks outperforming their industry average and maintaining a high risk_reward profile
    sector_leaders = df[(df['rel_strength_ind'] > 0) & (df['over_pc'] > 0)].copy()
    
    # Sort by relative strength and risk_reward to find the best leaders
    sector_leaders.sort_values(by=['rel_strength_ind', 'risk_reward'], ascending=[False, False], inplace=True)
    
    # Display Top 20 Sector Leaders
    display_df = sector_leaders[['sector', 'industry', 'symbol', 'over_pc', 'ind_mean_pc', 'rel_strength_ind', 'risk_reward']].head(50)
    display(display_df.head(5))
    worksheet_update_with_df(workbook_name, worksheet_id, display_df)
""")
]
with open('1_Relative_Strength_Sector_Leadership.ipynb', 'w') as f:
    nbf.write(nb1, f)


# ==========================================
# Notebook 2: Quality of Trend
# ==========================================
nb2 = nbf.v4.new_notebook()
nb2['cells'] = [
    nbf.v4.new_markdown_cell("# Quality of Trend (Consistency vs. One-Hit Wonders)\nThis notebook identifies steady, compounding uptrends by finding stocks with high overall performance (`over_pc`), high daily consistency (`pc_mean`), and crucially, very low volatility (`pc_std`). This weeds out stocks whose gains came from a single massive, erratic gap-up."),
    nbf.v4.new_code_cell(setup_code_1),
    nbf.v4.new_code_cell(f"""\
workbook_name = 'Quality Of Trend Consistency'
{loop_code_start}
    # 1. Filter out excessively volatile stocks
    # We find the median volatility to establish a baseline
    median_std = df['pc_std'].median()
    
    # A strong quality trend stock should have solid overall returns but below-average, or contained, volatility
    steady_trends = df[(df['over_pc'] > 0) & (df['pc_std'] < (median_std * 1.5))].copy()
    
    # 2. We can score "Consistency" as simply returning the lowest possible std for the highest possible mean
    top_quartile_perf = steady_trends['over_pc'].quantile(0.75)
    best_consistent_trends = steady_trends[steady_trends['over_pc'] >= top_quartile_perf].copy()
    
    # Sort by least volatile first, then highest risk_reward
    best_consistent_trends.sort_values(by=['pc_std', 'over_pc'], ascending=[True, False], inplace=True)
    
    # Select columns to display
    display_df = best_consistent_trends[['sector', 'industry', 'symbol', 'over_pc', 'pc_mean', 'pc_std', 'risk_reward']].head(50)
    display(display_df.head(5))
    worksheet_update_with_df(workbook_name, worksheet_id, display_df)
""")
]
with open('2_Quality_Of_Trend_Consistency.ipynb', 'w') as f:
    nbf.write(nb2, f)


# ==========================================
# Notebook 3: Probability of a Positive Day
# ==========================================
nb3 = nbf.v4.new_notebook()
nb3['cells'] = [
    nbf.v4.new_markdown_cell("# Probability of a Positive Day\nBy treating the daily returns as a normal distribution utilizing the `pc_mean` and `pc_std`, we can model the statistical probability that the stock will close 'green' on any randomly given trading day."),
    nbf.v4.new_code_cell(setup_code_1),
    nbf.v4.new_code_cell(f"""\
import scipy.stats as stats

workbook_name = 'Probability Of Positive Day'
{loop_code_start}
    # Ensure we don't have zeros in our standard deviation (which would break division)
    df_prob = df[df['pc_std'] > 0].copy()
    
    # Calculate the Survival Function (1 - CDF) at 0.0 % using the mean and standard deviation.
    # This essentially gives us P(X > 0)
    df_prob['prob_green_day'] = stats.norm.sf(0, loc=df_prob['pc_mean'], scale=df_prob['pc_std'])
    
    # Convert to a readable percentage format
    df_prob['prob_green_day_%'] = (df_prob['prob_green_day'] * 100).round(2)
    
    # Sort by the highest probability of closing green
    df_prob.sort_values(by='prob_green_day', ascending=False, inplace=True)
    
    # Select columns to display
    display_df = df_prob[['sector', 'industry', 'symbol', 'pc_mean', 'pc_std', 'prob_green_day_%']].head(50)
    display(display_df.head(5))
    worksheet_update_with_df(workbook_name, worksheet_id, display_df)
""")
]
with open('3_Probability_Of_Positive_Day.ipynb', 'w') as f:
    nbf.write(nb3, f)


# ==========================================
# Notebook 4: Mean Reversion / Rubber Band
# ==========================================
nb4 = nbf.v4.new_notebook()
nb4['cells'] = [
    nbf.v4.new_markdown_cell("# Mean Reversion (Rubber Band Indicator)\nWhen a stock's overall performance drastically exceeds what is statistically normal given its historical standard deviation, it is over-extended. High anomalous spikes signal a rubber band that is stretched out and vulnerable to snapping back (Mean Reversion)."),
    nbf.v4.new_code_cell(setup_code_1),
    nbf.v4.new_code_cell(f"""\
workbook_name = 'Mean Reversion Rubber Band'
{loop_code_start}
    df_mr = df[df['pc_std'] > 0].copy()
    
    df_mr['stretch_score'] = df_mr['over_pc'] / df_mr['pc_std']
    
    # Over-extended stocks (Stretched to the upside)
    over_extended = df_mr.sort_values(by='stretch_score', ascending=False)
    
    print("--- TOP OVER-EXTENDED STOCKS (Vulnerable to Pullback) ---")
    display_oe = over_extended[['sector', 'industry', 'symbol', 'over_pc', 'pc_std', 'stretch_score']].head(50)
    display(display_oe.head(5))
    
    # Oversold / Capitulated stocks (Stretched to the downside)
    oversold = df_mr.sort_values(by='stretch_score', ascending=True)
    
    print("\\n--- TOP OVERSOLD STOCKS (Vulnerable to Bounce) ---")
    display_os = oversold[['sector', 'industry', 'symbol', 'over_pc', 'pc_std', 'stretch_score']].head(50)
    display(display_os.head(5))
    
    # We will upload the over_extended to the google sheet.
    worksheet_update_with_df(workbook_name, worksheet_id, display_oe)
""")
]
with open('4_Mean_Reversion_Rubber_Band.ipynb', 'w') as f:
    nbf.write(nb4, f)


# ==========================================
# Notebook 5: Kelly Criterion
# ==========================================
nb5 = nbf.v4.new_notebook()
nb5['cells'] = [
    nbf.v4.new_markdown_cell("# Kelly Criterion (Optimal Sizing)\nThe Kelly Criterion is a famous mathematical formula used to determine optimal bet sizing. It aggressively penalizes variance. The simplified continuous Kelly fraction is `Mean / Variance` (or `Mean / Std^2`). It outputs an 'Aggressiveness Score'."),
    nbf.v4.new_code_cell(setup_code_1),
    nbf.v4.new_code_cell(f"""\
workbook_name = 'Kelly Criterion Optimal Sizing'
{loop_code_start}
    # Ensure standard deviation is > 0
    df_kelly = df[df['pc_std'] > 0].copy()
    
    # Calculate Variance (Std Dev squared)
    df_kelly['pc_var'] = df_kelly['pc_std'] ** 2
    
    # Calculate the simplified Kelly Fraction (Mean / Variance)
    df_kelly['kelly_fraction'] = df_kelly['pc_mean'] / df_kelly['pc_var']
    
    # Filter out negative expectations
    df_kelly_positive = df_kelly[df_kelly['kelly_fraction'] > 0].copy()
    
    # Sort by the highest optimal sizing score
    df_kelly_positive.sort_values(by='kelly_fraction', ascending=False, inplace=True)
    
    display_df = df_kelly_positive[['sector', 'industry', 'symbol', 'pc_mean', 'pc_std', 'kelly_fraction']].head(50)
    display(display_df.head(5))
    worksheet_update_with_df(workbook_name, worksheet_id, display_df)
""")
]
with open('5_Kelly_Criterion_Optimal_Sizing.ipynb', 'w') as f:
    nbf.write(nb5, f)

print("Successfully generated all 5 Jupyter Notebooks in the current directory.")
