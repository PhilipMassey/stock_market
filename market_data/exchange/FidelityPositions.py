
import pandas as pd
import market_data as md
import os
from os.path import isfile, join
import glob

class FidelityPositions:
    def __init__(self):
        self.filepath = md.fidelity_positions_filep()
        self.df = None
        self.sum_df = None
        self.column_order = ['Symbol','Buy/Sell$','Current Value','Current Return%','Rating','Current Value %','Holding %','Buy/Sell %','Cost Basis Total','Quantity','Average Cost Basis']

    def execute(self):
        self.df_fidelity_positions()
        self.df_aggregate_columns()
        #self.df_calculate_current_return()
        self.order_columns()
        portfolio = 'Alpha Picks'
        directory = md.proforma
        self.filter_to_portfolio_and_file(directory, portfolio)
        portfolio = 'Dividends'
        directory = md.proforma
        self.filter_to_portfolio_and_file(directory, portfolio)
        portfolio = 'ETFs'
        directory = md.proforma
        self.filter_to_portfolio_and_file(directory, portfolio)
        portfolio = 'Stocks'
        directory = md.proforma
        self.filter_to_portfolio_and_file(directory, portfolio)

    def df_fidelity_positions(self):
        self.df = md.df_from_cvs(self.filepath, column_names=['Account Name', 'Symbol', 'Current Value', 'Cost Basis Total', 'Quantity', 'Average Cost Basis'])
        md.df_strip_character_from_colvals(self.df ,'Current Value')
        md.df_strip_character_from_colvals(self.df, 'Cost Basis Total')
        md.df_strip_character_from_colvals(self.df, 'Average Cost Basis')
        self.money_market()
        self.df = self.df.dropna()

    def df_aggregate_columns(self):
        self.sum_df = self.df.groupby('Symbol').agg(
            {'Current Value': 'sum', 'Cost Basis Total': 'sum', 'Quantity': 'sum', 'Average Cost Basis': 'mean'})
        self.sum_df['Average Cost Basis'] = self.sum_df['Average Cost Basis'].apply(lambda x: round(x, 2))
        self.sum_df.reset_index(inplace=True)
        self.sum_df = self.sum_df.rename(columns={'index': 'Symbol'})


    def money_market(self):
        filter_values = ['FDRXX', 'SPAXX', 'Pending Activity']
        mmdf = self.df_filter_to_symbols( filter_values)
        #mmdf = mmdf.groupby('Symbol').agg({'Current Value':sum})
        mmdf = mmdf.groupby('Symbol').agg({'Current Value': 'sum'})
        mmdf.reset_index(inplace=True)
        mmdf.rename(columns={'index':'Symbol'}, inplace=True)
        filep = join(md.download_dir, md.fidelity_postions, ' Money Market.txt')
        md.write_df_to_file(mmdf, filep)

    def df_filter_to_symbols(self, filter_values):
        filtered_df = self.df[self.df['Symbol'].str.contains('|'.join(filter_values))]
        return filtered_df

    def df_calculate_current_return(self):
        difference_list = self.sum_df['Current Value'] - self.sum_df['Cost Basis Total']
        percent_difference = (difference_list / self.sum_df['Current Value']) # * 100).apply(lambda x: round(x, 2))
        self.sum_df['Current Return %'] = percent_difference
        self.sum_df['Current Return %'] = (self.sum_df['Current Return %'] *100).map('{:.2f}'.format)

    def filter_to_portfolio_and_file(self, directory, portfolio):
        df_filtered = self.df_filter_to_portfolio(directory, portfolio)
        filep = join(md.download_dir, md.fidelity_postions, portfolio + '.xlsx')
        df_filtered.to_excel(filep)

    def df_calculate_percent_of_total(self,col_name, col_perc_name):
        cv_sum = self.df[col_name].sum()
        self.df[col_perc_name] = (self.df[col_name] / cv_sum) #* 100
        #self.df[col_perc_name] = self.df[col_perc_name].apply(lambda x: round(x, 2))
        df[col_perc_name] = (df[col_perc_name] * 100).map('{:.2f}%'.format)


    def df_filter_to_portfolio(self, directory, portfolio):
        symbols = md.get_symbols_dir_and_port(directory, portfolio)
        df_filtered = self.sum_df[self.sum_df.Symbol.isin(symbols)].sort_values('Symbol')
        md.df_calculate_percent_of_total(df_filtered, 'Current Value', 'Current Value %')
        symbols = md.get_symbols_dir_and_port(directory, portfolio)
        df_p = pd.DataFrame(symbols,columns=['Symbol'])
        df_filtered = pd.merge(df_filtered, df_p, on='Symbol', how='outer').sort_values(by=['Symbol'])
        return df_filtered

    def order_columns(self):
        self.sum_df = self.sum_df.reindex(columns=self.column_order)

    def print_differences(self):
        symbols = set(md.get_symbols(md.proforma))
        sumd_df_symbols = set(self.sum_df.Symbol.values)
        print('more in fidelity \n', sumd_df_symbols.difference(symbols))
        print('more in proforma \n', symbols.difference(sumd_df_symbols))
        filep = join(md.download_dir, md.fidelity_postions, 'Missing Fidelity Porsitions.txt')
        md.write_list_to_file(filep, sorted(symbols.difference(sumd_df_symbols)))