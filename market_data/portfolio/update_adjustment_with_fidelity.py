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
        df = fidelity_df[fidelity_df['Account Name']==portfolio]
        df = df[['Symbol', 'Current Value', 'Cost Basis Total']]
        current_total = round(sum(df['Current Value']),2)
        cost_basis_total = round(sum(df['Cost Basis Total']),2)
        df['Current Value %'] = (df['Current Value']/current_total) #*100
        df['Current Return %'] = ((df['Current Value'] - df['Cost Basis Total']) / df['Cost Basis Total']) #* 100
        df_update = df[['Symbol', 'Current Value %','Current Return %']]
        worksheet_id = md.dct_adjustment_id[portfolio]
        # FIX: Replace Infinity with NaN, then replace all NaNs with an empty string (or 0)
        df_update = df_update.replace([np.inf, -np.inf], np.nan)
        df_update = df_update.fillna('')  # Use '' for blank cells or 0 for zeros

        result = md.worksheet_update_with_df(workbook_name, worksheet_id, df_update)

if __name__ == '__main__':
    fidelity_df = md.df_fidelity_portfolios()
    adjustments_update_fidelity_percentages(fidelity_df)