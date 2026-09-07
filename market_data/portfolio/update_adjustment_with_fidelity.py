import market_data as md
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
gc = gspread.service_account(filename='/Users/philipmassey/.config/gspread/service_account.json')
import numpy as np

def adjustments_update_fidelity_percentages(fidelity_df):
    workbook_name = md.portfolio_adjustments
    for portfolio in md.portfolios:
        print(portfolio)
        df = fidelity_df[fidelity_df['Account name']==portfolio]
        df = df[['Symbol', 'Current value', 'Cost basis total']]
        current_total = round(sum(df['Current value']),2)
        cost_basis_total = round(sum(df['Cost basis total']),2)
        df['Current value %'] = (df['Current value']/current_total) #*100
        df['Current return %'] = ((df['Current value'] - df['Cost basis total']) / df['Cost basis total']) #* 100
        df_update = df[['Symbol', 'Current value %','Current return %']]
        worksheet_id = md.dct_adjustment_id[portfolio]
        # FIX: Replace Infinity with NaN, then replace all NaNs with an empty string (or 0)
        df_update = df_update.replace([np.inf, -np.inf], np.nan)
        df_update = df_update.fillna('')  # Use '' for blank cells or 0 for zeros

        result = md.worksheet_update_with_df(workbook_name, worksheet_id, df_update)

def compare_current_and_fidelity():
    seeking_symbols = []
    for port in md.portfolios:
        seeking_symbols.extend(md.get_symbols_dir_and_port(md.sa, 'Current ' + port))
    seeking_symbols = set(seeking_symbols)
    fidelity_symbols = set(md.get_symbols(md.holding))
    print('fidelity extras ', fidelity_symbols.difference(seeking_symbols))
    print('seeking extras ', seeking_symbols.difference(fidelity_symbols))

if __name__ == '__main__':
    fidelity_df = md.df_fidelity_portfolios()
    adjustments_update_fidelity_percentages(fidelity_df)
    compare_current_and_fidelity()