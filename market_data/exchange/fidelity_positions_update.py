import glob
from datetime import datetime
import market_data as md
import pandas as pd
from os.path import join

def fidelity_positions_filep():
    download_dir = md.download_dir
    files = glob.glob(download_dir + '/Portfolio_Positions*.csv')
    if len(files) != 1:
        raise Exception("File size is not 1")
    fn = files[0]
    date_str = fn[-15:].rsplit('.', 1)[0]
    adate = datetime.strptime(date_str, '%b-%d-%Y')
    return files[0], adate


def holding_portfolios_update():
    filep, adate = md.fidelity_positions_filep()
    df = pd.read_csv(filep)
    df = df.dropna()
    df = df[['Account Name', 'Symbol']]
    path = join(md.data_dir, 'holding')
    account_names = list(set(df['Account Name'].values))
    shorts = set(md.get_symbols_dir_and_port(directory='ETF', port='Short ETFs'))
    md.file_df_account_symbols(df, account_names, shorts, path)
    print('Completed Filing Holding Symbols ', path)


def file_df_account_symbols(df, account_names, shorts, path):
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
def money_market():
    filep, adate = md.fidelity_positions_filep()
    df = pd.read_csv(filep)
    df = df.dropna(how='all', subset=['Symbol'])
    df['Current Value'] = df['Current Value'].str.replace('$', '').astype(float)
    filter_values = ['FDRXX', 'SPAXX', 'Pending Activity']
    df = df[df['Symbol'].str.contains('|'.join(filter_values))]
    sum_df = df.groupby('Symbol').agg({'Current Value': 'sum'})
    total_current_value = df['Current Value'].sum()
    new_row = {'Account Name': 'Total', 'Current Value': total_current_value}
    new_row_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_row_df], ignore_index=True)
    df = df[['Account Name', 'Current Value']]
    filep = join(md.download_dir, ' Money Market.txt')
    md.write_df_to_file(df, filep)
    print('Completed Filing Money Market ', filep)

def df_fidelity_positions_aggregate_columns(df):
    dollar_cols =  ['Current Value', 'Cost Basis Total']
    for col in dollar_cols:
        df[col] = df[col].str.replace('$', '').astype(float)
    agg_df = df.groupby('Symbol').agg(
        {'Current Value': 'sum', 'Cost Basis Total': 'sum'})
    agg_df.reset_index(inplace=True)
    agg_df = agg_df.rename(columns={'index': 'Symbol'})
    return agg_df



def add_to_mdb():
    filep, adate = md.fidelity_positions_filep()
    df = pd.read_csv(filep)
    df = df_fidelity_positions_aggregate_columns(df)
    md.df_add_adate_column(adate, df)
    db_coll_name = md.db_fidel_pos
    md.add_df_to_db(df, db_coll_name)
    print('Positions added to:', db_coll_name)

if __name__ == '__main__':
    add_to_mdb()
    holding_portfolios_update()
    money_market()