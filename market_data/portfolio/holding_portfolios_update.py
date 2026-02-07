import market_data as md
import pandas as pd
from os.path import join
import glob
from datetime import datetime


def fidelity_positions_filep():
    download_dir = md.download_dir
    files = glob.glob(download_dir + '/Portfolio_Positions*.csv')
    if len(files) != 1:
        raise Exception("File size is not 1")
    fn = files[0]
    date_str = fn[-15:].rsplit('.', 1)[0]
    a_date = datetime.strptime(date_str, '%b-%d-%Y')
    return a_date, files[0]


def df_fidelity_positions_portfolio():
    a_date, filep = fidelity_positions_filep()
    fidelity_df = pd.read_csv(filep, header=0, index_col=False)
    fidelity_df = fidelity_df.dropna(how='all', subset=['Symbol'])
    fidelity_df['Symbol'] = fidelity_df['Symbol'].replace('Pending Activity', 'FDRXX**')
    return a_date, fidelity_df


def df_fidelity_positions_aggregate_columns(df):
    dollar_cols = ['Current Value', 'Cost Basis Total', 'Average Cost Basis', 'Last Price']
    for col in dollar_cols:
        df[col] = df[col].str.replace('$', '').astype(float)
    percent_cols = ['Percent Of Account']
    for col in percent_cols:
        df[col] = df[col].str.replace('%', '').astype(float)

    agg_df = df.groupby('Symbol').agg(
        {'Account Name': 'first', 'Quantity': 'sum', 'Current Value': 'sum', 'Cost Basis Total': 'sum',
         'Last Price': 'first', 'Average Cost Basis': 'mean', 'Percent Of Account': 'mean'})
    agg_df.reset_index(inplace=True)
    agg_df = agg_df.rename(columns={'index': 'Symbol'})
    return agg_df


def fidelity_positions_worksheet_update():
    a_date, df = df_fidelity_positions_portfolio()
    df = df_fidelity_positions_aggregate_columns(df)
#    df['Current Return %'] = 0
#    df['Current Value %'] = 0
    df = df.drop(df[df[['Symbol']].applymap(lambda x: '*' in str(x)).any(axis=1)].index)
    df = df[df['Symbol'] != 'Pending activity']
    workbook_name = 'Portfolio Adjustments'
    worksheet_id = md.dct_adjustment_id['Fidelity Positions']
    result = md.worksheet_update_with_df(workbook_name, worksheet_id, df)
    print('Fidelity Positions worksheet update: ', result)
    return result


def df_fidelity_portfolios():
    #a_date, file_p = md.fidelity_positions_filep()
    #fidelity_df = pd.read_csv(file_p)
    a_date, fidelity_df = df_fidelity_positions_portfolio()
    fidelity_df = fidelity_df[fidelity_df['Symbol'] != 'CORE**']
    fidelity_df = fidelity_df[fidelity_df['Symbol'] != 'FDRXX**']
    fidelity_df = fidelity_df[fidelity_df['Symbol'] != 'SPAXX**']
    fidelity_df = fidelity_df[fidelity_df['Symbol'] != 'Pending activity']
    fidelity_df['Account Name'] = fidelity_df['Account Name'].replace(['X Stocks', 'Stocks'], 'Stocks')
    fidelity_df['Account Name'] = fidelity_df['Account Name'].replace(['Z Dividends', 'Dividends'], 'Dividends')
    fidelity_df['Account Name'] = fidelity_df['Account Name'].replace(['Z ETFs', 'ETFs Roth'], 'ETFs')
    fidelity_df['Account Name'] = fidelity_df['Account Name'].replace(['Z Shorts', 'Shorts'], 'Shorts')
    fidelity_df['Account Name'] = fidelity_df['Account Name'].replace(['International'], 'International')
    fidelity_df = df_fidelity_positions_aggregate_columns(fidelity_df)
    return fidelity_df

def file_df_account_symbols(df, account_names, path):
    suffix = '.csv'
    for account in account_names:
        if isinstance(account, str):
            symbols = sorted((df[df['Account Name'] == account].Symbol.values))
            fpath = join(path, account + suffix)
            with open(fpath, 'w') as f:
                f.write('Symbol\n' + '\n'.join(symbols))
                f.close()


def market_data_holding_portfolios_update(fidelity_df):
    df = fidelity_df[['Account Name', 'Symbol']]
    path = join(md.data_dir, 'holding')
    account_names = list(set(df['Account Name'].values))
    file_df_account_symbols(df, account_names, path)
    print('Completed Filing Holding Symbols ', path)
    return path

def money_market():
    a_date, fidelity_df = df_fidelity_positions_portfolio()
    fidelity_df['Current Value'] = fidelity_df['Current Value'].str.replace('$', '').astype(float)
    #df = df_agg_on_symbol_from_fidelity_positions_csv()
    filter_values = ['FDRXX',"CORE", 'SPAXX','Pending activity']
    fidelity_df = fidelity_df[fidelity_df['Symbol'].str.contains('|'.join(filter_values))]
    fidelity_df = fidelity_df[['Account Name', 'Current Value']]
    fidelity_df = fidelity_df.groupby('Account Name').sum({'Current Value': 'sum'})
    total_current_value = fidelity_df['Current Value'].sum()
    new_row = {'Account Name': 'Total', 'Current Value': total_current_value}
    new_row_df = pd.DataFrame([new_row])
    fidelity_df.reset_index(inplace=True)
    fidelity_df = pd.concat([fidelity_df, new_row_df], ignore_index=True)
    filep = join(md.download_dir, 'Money Market.txt')
    md.write_df_to_file(fidelity_df, filep)
    print('Completed Filing Money Market: ', filep)

def add_fidelity_positions_to_mdb():
    adate, fidelity_df = df_fidelity_positions_portfolio()
    df_agg = df_fidelity_positions_aggregate_columns(fidelity_df)
    df_agg.fillna(0, inplace=True)
    df_agg.drop(df_agg[df_agg['Quantity'] == 0].index, inplace=True)
    df_agg['Date'] = adate
    db_coll_name = md.db_fidel_pos
    count = md.add_df_to_db(df_agg, db_coll_name)
    print('Positions added to mdb: ', count, db_coll_name)


if __name__ == '__main__':
    print('Updating from Fidelity csv ...')
    print('Fidelity Portfolio worksheet updating...')
    result = fidelity_positions_worksheet_update()
    fidelity_df = df_fidelity_portfolios()
    print('Holding portfolios updating...')
    path = market_data_holding_portfolios_update(fidelity_df)
    money_market()
    add_fidelity_positions_to_mdb()
