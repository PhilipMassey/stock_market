import market_data as md
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
gc = gspread.service_account(filename='/Users/philipmassey/.config/gspread/service_account.json')


def df_calculate_fidelity_percentages(fidelity_df):
    workbook_name = md.portfolio_adjustments
    for portfolio in md.portfolios:
        print(portfolio)
        df = fidelity_df[fidelity_df['Account Name']==portfolio]
        df = df[['Symbol', 'Current Value', 'Cost Basis Total']]
        current_total = round(sum(df['Current Value']),2)
        cost_basis_total = round(sum(df['Cost Basis Total']),2)
        df['Current Value %'] = (df['Current Value']/current_total) #*100
        df['Current Return %'] = ((df['Current Value'] - df['Cost Basis Total']) / df['Cost Basis Total']) #* 100
        df_update = df[['Symbol', 'Current Return %', 'Current Value %']]
        worksheet_id = md.dct_adjustment_id[portfolio]
        result = md.worksheet_update_with_df(workbook_name, worksheet_id, df_update)

if __name__ == '__main__':
    fidelity_df = md.df_fidelity_portfolios()
    df_calculate_fidelity_percentages(fidelity_df)