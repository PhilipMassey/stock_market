
import pandas as pd
import market_data as md
import os
from os.path import isfile, join

class FidelityPositions:
    """
    Load Fidelity Positions cvs into self.df and download to
    Aggreate Roll up symbols and
    Args:
        spreadsheet_url (str): The URL of the Google Spreadsheet.
        sheet_id (str): The ID of the specific sheet within the spreadsheet.
    Returns:
        pandas.DataFrame: The DataFrame created from the specified sheet.
    """
    def __init__(self):
        fpath, adate = md.fidelity_positions_filep()
        self.fidelity_positions_filep = fpath
        self.df = None
        self.adate = adate
        self.sum_df = None
        self.base_columns = ['Symbol','Current Value','Cost Basis Total','Quantity','Average Cost Basis']
        self.column_order = ['Symbol','Buy/Sell $','Current Value','Current Return %','Rating','Current Value %','Holding %','Buy/Sell %','Cost Basis Total','Quantity','Average Cost Basis']
        self.column_order = ['Symbol', 'Buy/Sell $', 'Current Value', 'Current Return %', 'Rating', 'Current Value %',
                             'Holding %', 'Buy/Sell %', 'Cost Basis Total', 'Quantity', 'Average Cost Basis']
        self.dollar_cols =  ['Current Value', 'Cost Basis Total',  'Average Cost Basis']
        self.dct_sheet_url = {
            'Portfolio Proforma': 'https://docs.google.com/spreadsheets/d/15FDENGNSt6n-iKfWwX9nqqrXVFwN5Cp0GWQXxlaw_x4/edit#gid=0',
            'Portfolio Adjustments': 'https://docs.google.com/spreadsheets/d/1bTsH3cjQDGR-Mlnq-bypRqhGIHJApKKJgsgXWSemur4/edit#gid=0'}
        self.dct_proforma_id = {'Alpha Picks': 1375800256, 'Dividends': 0, 'ETFs': 1884178483, 'International': 874195600,
                                'Stocks': 462380812, 'Treasuries': 335039254}
        self.dct_adjustment_id = {'Alpha Picks': 0, 'Dividends': 1022929694, 'ETFs': 84489004, 'International': 1766130281,
                                  'Stocks': 569122364, 'Treasuries': 1853636016, 'Fidelity Positions': 1064903312}

    def df_fidelity_positions_load(self):
        df = pd.read_csv(self.fidelity_positions_filep)
        df = df.dropna()
        self.df = df


    def df_aggregate_columns(self):
        for col in self.dollar_cols:
            self.df[col] = self.df[col].str.replace('$', '').astype(float)
        self.df['Average Cost Basis'] = self.df['Average Cost Basis'].astype(str)
        self.df['Average Cost Basis'] = self.df['Average Cost Basis'].str.replace('$', '').astype(float)
        self.sum_df = self.df.groupby('Symbol').agg(
            {'Current Value': 'sum', 'Cost Basis Total': 'sum', 'Quantity': 'sum', 'Average Cost Basis': 'mean'})
        self.sum_df['Average Cost Basis'] = self.sum_df['Average Cost Basis'].apply(lambda x: round(x, 2))
        self.sum_df.reset_index(inplace=True)
        self.sum_df = self.sum_df.rename(columns={'index': 'Symbol'})

    def fidelity_positions_worksheet_update(self):
        md.worksheet_update_with_df('Portfolio Adjustments', 'Fidelity Positions', self.sum_df)


    def order_and_add_columns(self):
        self.sum_df = self.sum_df.reindex(columns=self.column_order)
        for column in sum_df.columns:
            sum_df[column] = sum_df[column].fillna(0)



    def print_differences(self):
        symbols = set(md.get_symbols(md.proforma))
        sumd_df_symbols = set(self.sum_df.Symbol.values)
        print('Extra Fidelity Positions\n', sumd_df_symbols.difference(symbols))
        print('Extra Proforma Symbols\n', symbols.difference(sumd_df_symbols))
        filep = join(md.download_dir, md.fidelity_positions, 'Proforma not in Fidelity.txt')
        md.write_list_to_file(filep, sorted(symbols.difference(sumd_df_symbols)))


