import pandas as pd
import market_data as md
import os
from os.path import isfile, join
import glob
def df_fidelity_positions():
    filepath = md.fidelity_positions_filep()
    df = pd.read_csv(filepath)
    df = md.df_from_cvs(filepath, column_names=['Account Name', 'Symbol' ,'Current Value' ,'Cost Basis Total' ,'Quantity'
                                      ,'Average Cost Basis'])

    md.df_strip_character_from_colvals(df ,'Current Value')
    md.df_strip_character_from_colvals(df, 'Cost Basis Total')
    md.df_strip_character_from_colvals(df, 'Average Cost Basis')
    money_market(df)
    df = df.dropna()
    return df


def money_market(df):
    filter_values = ['FDRXX', 'SPAXX', 'Pending Activity']
    df = df[df['Symbol'].str.contains('|'.join(filter_values))]
    df = df.groupby('Symbol').agg({'Current Value':sum})
    #df.reindex()
    df.reset_index(inplace=True)
    df.rename(columns={'index':'Symbol'},inplace=True)
    filep = join(md.download_dir, md.fidelity_postions,' Money Market Fidelity.txt')
    md.write_df_to_file(df, filep)





def df_calculate_percent_of_total(df, col_name, col_perc_name):
    cv_sum = df[col_name].sum()
    df[col_perc_name] = (df[col_name] / cv_sum)
    df[col_perc_name] = (df[col_perc_name] * 100).map('{:.2f}'.format)

def fidelity_positions_filep():
    download_dir = md.download_dir
    files = glob.glob(download_dir + '/Portfolio_Positions*.csv')
    if len(files) != 1:
        raise Exception("File size is not 1")
    return files[0]


def df_fidelity_positions():
    filepath = md.fidelity_positions_filep()
    df = pd.read_csv(filepath)
    df = md.df_from_cvs(filepath,
                        column_names=['Account Name', 'Symbol', 'Current Value', 'Cost Basis Total', 'Quantity',
                                      'Average Cost Basis'])
    md.df_strip_character_from_colvals(df, 'Current Value')
    md.df_strip_character_from_colvals(df, 'Cost Basis Total')
    md.df_strip_character_from_colvals(df, 'Average Cost Basis')
    money_market(df)
    df = df.dropna()
    return df

def df_filter_to_portfolio(df, directory, portfolio):
    symbols = md.get_symbols_dir_and_port(directory, portfolio)
    df = df[df.Symbol.isin(symbols)].sort_values('Symbol')
    md.df_calculate_percent_of_total(df, 'Current Value', 'Current Value %')
    symbols = md.get_symbols_dir_and_port(md.sa, portfolio)
    df_p = pd.DataFrame(symbols,columns=['Symbol'])
    df = pd.merge(df, df_p, on='Symbol', how='outer').sort_values(by=['Symbol'])
    return df

def df_aggregate_columns(df):
    sum_df = df.groupby('Symbol').agg({'Current Value': 'sum', 'Cost Basis Total': 'sum', 'Quantity': 'sum', 'Average Cost Basis': 'mean'})
    sum_df['Average Cost Basis'] = sum_df['Average Cost Basis'].apply(lambda x: round(x, 2))
    sum_df.reset_index(inplace=True)
    sum_df = sum_df.rename(columns={'index': 'Symbol'})
    return sum_df

def df_calculate_current_return(sum_df):
    difference_list = sum_df['Current Value'] - sum_df['Cost Basis Total']
    percent_difference = (difference_list / sum_df['Current Value'])  # * 100).apply(lambda x: round(x, 2))
    sum_df['Current Return%'] = percent_difference
    sum_df['Current Return%'] = (sum_df['Current Return%']).map('{:.2f}%'.format)
    new_order = ['Symbol', 'Buy/Sell $', 'Current Value', 'Current Return %', 'Current Value %', 'Buy/Sell %',
                 'Cost Basis Total', 'Quantity', 'Average Cost Basis']
    sum_df = sum_df.reindex(columns=new_order)
    return sum_df

def filter_to_portfolio_and_file(sum_df, directory, portfolio):
    df_filtered = df_filter_to_portfolio(sum_df, directory, portfolio)
    # filep = join(md.download_dir, md.fidelity_postions, portfolio + ' Fidelity.txt')
    # md.write_df_to_file(df_filtered, filep)
    filep = join(md.download_dir, md.fidelity_postions, portfolio + '  Fidelity.xlsx')
    df_filtered.to_excel(filep)
