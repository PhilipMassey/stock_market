import os
import pandas as pd
import market_data as md
import math


def is_nan(value):
    return math.isnan(float(value))


def file_df_tickers(df, acount_names, path):
    suffix = '.csv'
    for account in acount_names:
        if isinstance(account, str):
            tickers = list(df[df['Account Name'] == account].Symbol.values)
            if 'FDRXX**' in tickers:
                tickers.remove('FDRXX**')
            if 'CORE**' in tickers:
                tickers.remove('CORE**')
            if 'Pending Activity' in tickers:
                tickers.remove('Pending Activity')
            if 'SPAXX**' in tickers:
                tickers.remove('SPAXX**')
            fpath = os.path.join(path, account + suffix)
            with open(fpath, 'w') as f:
                f.write('Ticker\n' + '\n'.join(tickers))
                f.close()
    print('completed: updating ', path)


def run_file_df_tickers(filename):
    filepath = os.path.join('/Users/philipmassey/Downloads/', filename)
    df = pd.read_csv(filepath)
    df = df[['Account Name', 'Symbol']]
    df_accounts = df.dropna()
    path = os.path.join(md.data_dir, 'holding')
    account_names = list(set(df['Account Name'].values))
    file_df_tickers(df_accounts, account_names, path)


if __name__ == '__main__':
    filename = 'Portfolio_Positions.csv'
    run_file_df_tickers(filename)