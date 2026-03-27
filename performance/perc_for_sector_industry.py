import market_data as md
import apis
import performance as pf
import pandas as pd
import numpy as np




def df_overall_performance(ndays_range, symbols):
    """
    Calculate performance metrics for symbols over a given date range.
    
    Returns a DataFrame with the following calculated columns:
    - over_pc: The overall percentage change.
    - pc_mean: The average period-to-period percentage change.
    - pc_std:  The standard deviation (volatility) of the period changes.
    - risk_reward: The ratio of mean return to standard deviation.
    """
    df_all = md.df_mdb_clossins_for_ndays_range(ndays_range, symbols)
    
    # Calculate overall percentage based on first valid and last valid price instead of blindly shifting periods
    first_valid = df_all.bfill().iloc[0]
    last_valid = df_all.ffill().iloc[-1]
    df_over_pct = ((last_valid - first_valid) / first_valid) * 100
    
    df_vars = pd.DataFrame(df_over_pct, columns=['over_pc'])
    
    # Calculate period pct change but immediately drop NaNs so mean/std aren't poisoned
    df_period_pct = df_all.pct_change(periods=1) * 100
    
    # Calculate metric ignoring NaNs
    df_vars['pc_mean'] = df_period_pct.mean()
    df_vars['pc_std'] = df_period_pct.std()
    
    # New: Risk-Reward Proxy (Simplified Sharpe)
    # Using np.where to avoid division by zero if a stock has 0 volatility
    df_vars['risk_reward'] = np.where(
        df_vars['pc_std'] != 0, 
        df_vars['pc_mean'] / df_vars['pc_std'], 
        0
    )
    
    df_vars.reset_index(inplace=True)
    df_vars.rename(columns={'index':'symbol'}, inplace=True)
    df_vars = df_vars.round(3)
    return df_vars




def df_overall_performance_sharpe_ratio(ndays_range, symbols, annual_rf_rate=0.04, periods_per_year=252):
    """
    Calculate performance metrics for symbols over a given date range.
    
    Parameters:
    - annual_rf_rate: The current annual risk-free rate (default 4%).
    - periods_per_year: 252 for daily data, 52 for weekly, 12 for monthly.
    """
    df_all = md.df_mdb_clossins_for_ndays_range(ndays_range, symbols)
    
    # 1. Overall Percentage Change
    first_valid = df_all.bfill().iloc[0]
    last_valid = df_all.ffill().iloc[-1]
    df_over_pct = ((last_valid - first_valid) / first_valid) * 100
    
    df_vars = pd.DataFrame(df_over_pct, columns=['over_pc'])
    
    # 2. Period Percentage Change (Returns are in %)
    df_period_pct = df_all.pct_change(periods=1) * 100
    
    df_vars['pc_mean'] = df_period_pct.mean()
    df_vars['pc_std'] = df_period_pct.std()
    
    # 3. Calculate True Annualized Sharpe Ratio
    # First, convert the annual risk-free rate (e.g., 0.04) to a daily percentage rate
    period_rf_pct = (annual_rf_rate / periods_per_year) * 100
    
    # Calculate the "Excess Return" (Stock Return - Risk Free Return)
    excess_return = df_vars['pc_mean'] - period_rf_pct
    
    # Calculate the ratio and annualize it by multiplying by sqrt(periods)
    df_vars['sharpe_ratio'] = np.where(
        df_vars['pc_std'] != 0, 
        (excess_return / df_vars['pc_std']) * np.sqrt(periods_per_year), 
        0
    )
    
    # 4. Cleanup
    df_vars.reset_index(inplace=True)
    df_vars.rename(columns={'index':'symbol'}, inplace=True)
    df_vars = df_vars.round(3) 
    
    return df_vars




def df_perc_by_sector_industry(ndays_range ,symbols ):
    fields = ['sectorname','primaryname','symbol']
    df = apis.df_symbol_profile(symbols, fields)
    df.dropna(inplace=True)
    return df



def df_secind_sym_perf(ndays_range, symbols):
    """
    Combines sector and industry info with the performance metrics.
    Retrieves the metrics calculated in df_overall_performance (over_pc, pc_mean, pc_std, risk_reward).
    """
    df_over_perf = df_overall_performance(ndays_range, symbols)
    # Get sector info without relying on ndays_range time parameter passing
    df_sector_ind = df_perc_by_sector_industry(ndays_range, symbols)
    df_sector_ind.rename(columns={'sectorname':'sector','primaryname':'industry'}, inplace=True)
    
    # Merge using a left join anchored on performance so we don't return phantom sector rows
    df_secind_sym_perf = df_over_perf.merge(df_sector_ind, on='symbol', how='left')
    
    # Handle NaNs from API mapping missing profiles
    df_secind_sym_perf['sector'] = df_secind_sym_perf['sector'].fillna('Unknown')
    df_secind_sym_perf['industry'] = df_secind_sym_perf['industry'].fillna('Unknown')
    
    cols = ['sector', 'industry', 'symbol','over_pc','pc_mean','pc_std','risk_reward']
    return df_secind_sym_perf[cols].sort_values(by=['sector', 'industry', 'symbol'])

def df_secind_sym_perf_sharpe_ratio(ndays_range, symbols):
    """
    Combines sector and industry info with the performance metrics.
    Retrieves the metrics calculated in df_overall_performance_sharpe_ratio (over_pc, pc_mean, pc_std, sharpe_ratio).
    """
    df_over_perf = df_overall_performance_sharpe_ratio(ndays_range, symbols)
    # Get sector info without relying on ndays_range time parameter passing
    df_sector_ind = df_perc_by_sector_industry(ndays_range, symbols)
    df_sector_ind.rename(columns={'sectorname':'sector','primaryname':'industry'}, inplace=True)
    
    # Merge using a left join anchored on performance so we don't return phantom sector rows
    df_secind_sym_perf = df_over_perf.merge(df_sector_ind, on='symbol', how='left')
    
    # Handle NaNs from API mapping missing profiles
    df_secind_sym_perf['sector'] = df_secind_sym_perf['sector'].fillna('Unknown')
    df_secind_sym_perf['industry'] = df_secind_sym_perf['industry'].fillna('Unknown')
    
    cols = ['sector', 'industry', 'symbol','over_pc','pc_mean','pc_std','sharpe_ratio']
    return df_secind_sym_perf[cols].sort_values(by=['sector', 'industry', 'symbol'])