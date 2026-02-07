#Download dividends transaction to csv files in directory 'Cloud Drive/investing/dividends/dividends year'
# Change the year In the Google 'Dividend' work book
# Add a new year sheet and add id to 'dct_dividends_worksheet_id'
# Create the pivot table with 3 columns, one for Symbol , one for Quarter, one for Dividend
import market_data as md
import pandas as pd
from os.path import join, isfile
from os import listdir
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import market_data as md
import gspread
from gspread_dataframe import get_as_dataframe# Authenticate with your Google account
gc = gspread.service_account(filename='/Users/philipmassey/.config/gspread/service_account.json')
dividends_dir = '/Users/philipmassey/Library/Mobile Documents/com~apple~CloudDocs/investing/dividends/'
workbook_name = 'Dividends'
dct_dividends_worksheet_id={'2024':1040963489,'2025':1563512834}
year = '2024'
worksheet_id = dct_dividends_worksheet_id[year]



def df_sum_symbol_div_amount(quarter,year):
    fname = 'Accounts_History Q{}.csv'.format(quarter)
    fpath = join(path, fname)
    df = pd.read_csv(fpath)
    df['Dividend'] = df['Amount ($)']
    df = df.groupby('Symbol').agg({'Dividend': 'sum'})
    df.reset_index(inplace=True)
    df['Quarter'] = '{} {}'.format(quarter,year)
    return df[['Quarter','Symbol','Dividend']]

df_all = pd.DataFrame({})
for q in range(1,5):
    df = df_sum_symbol_div_amount(q,year)
    df_all = pd.concat([df_all, df])

print(df_all[0:5])

md.worksheet_update_with_df(workbook_name, worksheet_id, df_all)

