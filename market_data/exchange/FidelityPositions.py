
import pandas as pd
import market_data as md
import os
from os.path import isfile, join
import glob

class FidelityPositions:
    def __init__(self):
        self.filepath = md.fidelity_positions_filep()
        self.df = pd.read_csv(self.filepath)

    def df_fidelity_positions(self):
        self.df = md.df_from_cvs(self.filepath, column_names=['Account Name', 'Symbol', 'Current Value', 'Cost Basis Total', 'Quantity', 'Average Cost Basis'])
        md.df_strip_character_from_colvals(self.df ,'Current Value')
        md.df_strip_character_from_colvals(self.df, 'Cost Basis Total')
        md.df_strip_character_from_colvals(self.df, 'Average Cost Basis')
        self.money_market()
        self.df = self.df.dropna()
        return self.df

    def money_market(self):
        filter_values = ['FDRXX', 'SPAXX', 'Pending Activity']
        self.df = md.df_filter_to_symbols(self.df, filter_values)
        self.df = self.df.groupby('Symbol').agg({'Current Value':sum})
        self.df.reset_index(inplace=True)
        self.df.rename(columns={'index':'Symbol'}, inplace=True)
        filep = join(md.download_dir, md.fidelity_postions, ' Money Market Fidelity.txt')
        md.write_df_to_file(self.df, filep)

    def df_calculate_percent_of_total(self, col_name, col_perc_name):
        cv_sum = self.df[col_name].sum()
        self.df[col_perc_name] = (self.df[col_name] / cv_sum) * 100
        self.df[col_perc_name] = self.df[col_perc_name].apply(lambda x: round(x, 2))

    def fidelity_positions_filep(self):
        download_dir = md.download_dir
        files = glob.glob(download_dir + '/Portfolio_Positions*.csv')
        if len(files) != 1:
            raise Exception("File size is not 1")
        return files[0]

    def df_filter_to_symbols(self, filter_values):
        filtered_df = self.df[self.df['Symbol'].str.contains('|'.join(filter_values))]
        return filtered_df

    def get_symbols_dir_and_port(self, directory, portfolio):
        # Implementation for get_symbols_dir_and_port method is missing in the provided code

    # Add other methods as needed

# Usage example
fidelity = FidelityPositions()
df = fidelity.df_fidelity_positions()
