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

def df_fidelity_positions_portfolio():
    filep, adate = md.fidelity_positions_filep()
    positions_df = pd.read_csv(filep)
    positions_df = positions_df.dropna(how='all', subset=['Symbol'])
    positions_df['Symbol'] = positions_df['Symbol'].replace('Pending Activity', 'FDRXX**')
    return positions_df

def df_agg_on_symbol_from_fidelity_positions_csv():
    filep, adate = fidelity_positions_filep()
    #df = pd.read_csv(filep)
    df = df_fidelity_positions_portfolio()
    df = df_fidelity_positions_aggregate_columns(df)
    return adate, df



def market_data_holding_portfolios_update():
    #filep, adate = fidelity_positions_filep()
    #df = pd.read_csv(filep)
    df = df_fidelity_positions_portfolio()
    df = df[['Account Name', 'Symbol']]
    df = df.drop(df[df[['Symbol']].applymap(lambda x: '*' in str(x)).any(axis=1)].index)
    path = join(md.data_dir, 'holding')
    account_names = list(set(df['Account Name'].values))
    file_df_account_symbols(df, account_names, path)
    #print('Completed Filing Holding Symbols ', path)
    return path


def file_df_account_symbols(df, account_names, path):
    suffix = '.csv'
    for account in account_names:
        if isinstance(account, str):
            symbols = sorted((df[df['Account Name'] == account].Symbol.values))
            fpath = join(path, account + suffix)
            with open(fpath, 'w') as f:
                f.write('Symbol\n' + '\n'.join(symbols))
                f.close()
def money_market():
    #filep, adate = fidelity_positions_filep()
    #df = pd.read_csv(filep)
    #df = df.dropna(how='all', subset=['Symbol'])
    df = df_fidelity_positions_portfolio()
    df['Current Value'] = df['Current Value'].str.replace('$', '').astype(float)
    #df = df_agg_on_symbol_from_fidelity_positions_csv()
    filter_values = ['FDRXX',"CORE", 'SPAXX'] #'Pending Activity']
    df = df[df['Symbol'].str.contains('|'.join(filter_values))]
    df = df[['Account Name', 'Current Value']]
    df = df.groupby('Account Name').sum({'Current Value': 'sum'})
    total_current_value = df['Current Value'].sum()
    new_row = {'Account Name': 'Total', 'Current Value': total_current_value}
    new_row_df = pd.DataFrame([new_row])
    df.reset_index(inplace=True)
    df = pd.concat([df, new_row_df], ignore_index=True)
    filep = join(md.download_dir, 'Money Market.txt')
    md.write_df_to_file(df, filep)
    print('Completed Filing Money Market: ', filep)


def df_fidelity_positions_aggregate_columns(df):
    dollar_cols = ['Current Value', 'Cost Basis Total', 'Average Cost Basis', 'Last Price']
    for col in dollar_cols:
        df[col] = df[col].str.replace('$', '').astype(float)
    percent_cols = ['Percent Of Account']
    for col in percent_cols:
        df[col] = df[col].str.replace('%', '').astype(float)

    agg_df = df.groupby('Symbol').agg(
        {'Quantity': 'sum', 'Current Value': 'sum', 'Cost Basis Total': 'sum', 'Last Price': 'first',
         'Cost Basis Total': 'sum', 'Average Cost Basis': 'mean', 'Percent Of Account': 'mean'})
    agg_df.reset_index(inplace=True)
    agg_df = agg_df.rename(columns={'index': 'Symbol'})
    return agg_df

def df_read_fidelity_csv():
    filep, adate = md.fidelity_positions_filep()
    fidelity_df = pd.read_csv(filep)
    fidelity_df.fillna(0, inplace=True)
    return adate, fidelity_df


def add_fidelity_positions_to_mdb():
    adate, fidelity_df = df_read_fidelity_csv()
    df_agg = df_fidelity_positions_aggregate_columns(fidelity_df)
    df_agg.fillna(0, inplace=True)
    df_agg.drop(df_agg[df_agg['Quantity'] == 0].index, inplace=True)
    df_agg['Date'] = adate
    db_coll_name = md.db_fidel_pos
    count = md.add_df_to_db(df_agg, db_coll_name)
    print('Positions added to mdb: ', count, db_coll_name)


def print_fidelity_differences():
    proforma_symbols = set(md.get_symbols(md.proforma))
    filep, adate = fidelity_positions_filep()
    fidelity_df = pd.read_csv(filep)
    fidelity_df = df_fidelity_positions_aggregate_columns(fidelity_df)
    fidelity_symbols = set(fidelity_df.Symbol.values)
    fset = sorted(fidelity_symbols.difference(proforma_symbols))
    pset = sorted(proforma_symbols.difference(fidelity_symbols))
    print('Extra Fidelity Positions\n', fset)
    print('Extra Proforma Symbols\n', pset)
    filep = join(md.download_dir, 'Proforma not in Fidelity.txt')
    md.write_list_to_file(filep, 'Extra Fidelity Positions\n' + ', '.join(fset) + '\nExtra Proforma Symbols\n' + ', '.join(pset)) #sorted(fset|pset)

def write_fidelity_positions_portfolio(portfolio_names):
    positions_df = df_fidelity_positions_portfolio()
    dollar_cols =  ['Current Value','Cost Basis Total','Average Cost Basis']
    for col in dollar_cols:
        positions_df[col] = positions_df[col].str.replace('$', '').astype(float)
    positions_df = positions_df.groupby('Symbol').agg(
        {'Current Value':'sum','Cost Basis Total': 'sum', 'Quantity':'sum', 'Average Cost Basis':'mean'}).reset_index()
    df = pd.DataFrame({}, columns=['Symbol','Current Value',  'Cost Basis Total',  'Quantity',  'Average Cost Basis'])
    for portfolio_name in portfolio_names:
        proforma_df = md.df_from_google_spreadsheet(md.portfolio_proforma, md.dct_proforma_id[portfolio_name])
        filtered_df = positions_df[positions_df['Symbol'].isin(proforma_df.Symbol)]
        df = pd.concat([df, filtered_df], ignore_index=False)
    filep = join(md.download_dir, 'Dividends numbers.txt')
    md.write_df_to_file(df, filep)
    print('Completed Filing ','dividend numbers', ': ', filep)

def df_resolve_alpha_picks_proforma():
    df = md.df_from_google_spreadsheet(md.portfolio_proforma, md.dct_proforma_id['Alpha Picks'])
    df = df.drop(columns=df.columns[df.columns.str.contains('Unnamed')])
    df = df.dropna()
    df = df.groupby('Symbol').agg(
        {'Holding %': 'sum', 'Sector': 'first', 'Rating': 'first', 'Company': 'first', 'Picked': 'first',
         'Return': 'sum'}).reset_index()
    result = md.worksheet_update_with_df(md.portfolio_proforma,md.dct_proforma_id['Alpha Picks'],df)
    return df


if __name__ == '__main__':
    print('\tProforma Fidelity Positions worksheet updated.',result)
    result =market_data_holding_portfolios_update()
    print('\tHolding csv files updated.',result)
    md.df_resolve_alpha_picks_proforma()
    print('\tAlpha Picks worksheet removed duplicates')
    money_market()
    write_fidelity_positions_portfolio(['Dividends', 'Treasuries'])
    add_fidelity_positions_to_mdb()
    print_fidelity_differences()


