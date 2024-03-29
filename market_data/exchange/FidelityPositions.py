
import pandas as pd
import market_data as md
import os
from os.path import isfile, join
import glob
from datetime import datetime

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


    def df_fidelity_positions_load(self):
        df = pd.read_csv(self.fidelity_positions_filep)
        df = df.dropna()
        self.df = df


    def df_aggregate_columns(self):
        self.sum_df = self.df.groupby('Symbol').agg(
            {'Current Value': 'sum', 'Cost Basis Total': 'sum', 'Quantity': 'sum', 'Average Cost Basis': 'mean'})
        self.sum_df['Average Cost Basis'] = self.sum_df['Average Cost Basis'].apply(lambda x: round(x, 2))
        self.sum_df.reset_index(inplace=True)
        self.sum_df = self.sum_df.rename(columns={'index': 'Symbol'})

    def fidelity_positions_worksheet_update():
        spreadsheet_url = dct_sheet_url['Portfolio Adjustments']
        worksheet_id = dct_adjustment_id['Fidelity Positions']
        md.worksheet_update_with_df(spreadsheet_url, worksheet_id, df)

    def money_market(self):
        filter_values = ['FDRXX', 'SPAXX', 'Pending Activity']
        filtered_df = self.df[self.df['Symbol'].str.contains('|'.join(filter_values))]
        filtered_df = filtered_df.groupby('Symbol').agg({'Current Value': 'sum'})
        filtered_df.reset_index(inplace=True)
        filtered_df.rename(columns={'index':'Symbol'}, inplace=True)
        filep = join(md.download_dir, md.fidelity_positions, ' Money Market.txt')
        md.write_df_to_file(filtered_df, filep)

    #
    def order_columns(self):
        self.sum_df = self.sum_df.reindex(columns=self.column_order)

    def add_to_mdb(self):
        df = self.sum_df[['Symbol', 'Current Value', 'Cost Basis Total', 'Quantity', 'Average Cost Basis']]
        md.df_add_adate_column(self.adate, df)
        db_coll_name = md.db_fidel_pos
        md.add_df_to_db(df, db_coll_name)
        print('Positions added to:', db_coll_name)

    def print_differences(self):
        symbols = set(md.get_symbols(md.proforma))
        sumd_df_symbols = set(self.sum_df.Symbol.values)
        print('Extra Fidelity Positions\n', sumd_df_symbols.difference(symbols))
        print('Extra Proforma Symbols\n', symbols.difference(sumd_df_symbols))
        filep = join(md.download_dir, md.fidelity_positions, 'Proforma not in Fidelity.txt')
        md.write_list_to_file(filep, sorted(symbols.difference(sumd_df_symbols)))

    def file_df_account_symbols(self, df, account_names, shorts, path):
        suffix = '.csv'
        for account in account_names:
            if isinstance(account, str):
                symbols = (set(df[df['Account Name'] == account].Symbol.values))
                symbols = symbols.difference(shorts)
                symbols = sorted(list(symbols))
                fpath = join(path, account + suffix)
                with open(fpath, 'w') as f:
                    f.write('Symbol\n' + '\n'.join(symbols))
                    f.close()

    def holding_portfolios_update(self):
        df = pd.read_csv(self.fidelity_positions_filep)
        df = df.dropna()
        df = df[['Account Name', 'Symbol']]
        path = join(md.data_dir, 'holding')
        account_names = list(set(df['Account Name'].values))
        shorts = set(md.get_symbols_dir_and_port(directory='ETF', port='Short ETFs'))
        self.file_df_account_symbols(df, account_names, shorts, path)
        print('Completed Filing Holding Symbols ', path)


def fidelity_positions_filep():
    download_dir = md.download_dir
    files = glob.glob(download_dir + '/Portfolio_Positions*.csv')
    if len(files) != 1:
        raise Exception("File size is not 1")
    fn = files[0]
    date_str = fn[-15:].rsplit('.', 1)[0]
    adate = datetime.strptime(date_str, '%b-%d-%Y')
    return files[0], adate



#   def fidlelity_postions_xlsx_update(self):
#     directory = md.proforma
#     #save all
#     filep = join(md.download_dir, md.fidelity_positions, 'Fidelity Positions.xlsx')
#     self.sum_df.to_excel(filep)
#     portfolio = 'Alpha Picks'
#     self.filter_to_portfolio_and_file(directory, portfolio)
#     portfolio = 'Dividends'
#     self.filter_to_portfolio_and_file(directory, portfolio)
#     portfolio = 'ETFs'
#     self.filter_to_portfolio_and_file(directory, portfolio)
#     portfolio = 'Stocks'
#     self.filter_to_portfolio_and_file(directory, portfolio)
#     portfolio = 'International'
#     self.filter_to_portfolio_and_file(directory, portfolio)
#     portfolio = 'Treasuries'
#     self.filter_to_portfolio_and_file(directory, portfolio)
#     print('Completed Fidelity Positions xlsx')

#def df_filter_to_portfolio(self, directory, portfolio):
# symbols = md.get_symbols_dir_and_port(directory, portfolio)
#     df_filtered = self.sum_df[self.sum_df.Symbol.isin(symbols)].sort_values('Symbol')
#     symbols = md.get_symbols_dir_and_port(directory, portfolio)
#     df_p = pd.DataFrame(symbols,columns=['Symbol'])
#     df_filtered = pd.merge(df_filtered, df_p, on='Symbol', how='outer').sort_values(by=['Symbol'])
#     return df_filtered

# def filter_to_portfolio_and_file(self, directory, portfolio):
#     df_filtered = self.df_filter_to_portfolio(directory, portfolio)
#     filep = join(md.download_dir, md.fidelity_positions, portfolio + '.xlsx')
#     df_filtered.to_excel(filep)

  # def df_filter_to_symbols(self, filter_values):
    #     filtered_df = self.df[self.df['Symbol'].str.contains('|'.join(filter_values))]
    #     return filtered_df
