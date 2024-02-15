import os
import pandas as pd
import market_data as md
import math


def file_df_tickers(df, account_names, path):
    suffix = '.csv'
    for account in account_names:
        if isinstance(account, str):
            tickers = list(df[df['Account Name'] == account].Symbol.values)
            fpath = os.path.join(path, account + suffix)
            with open(fpath, 'w') as f:
                f.write('Ticker\n' + '\n'.join(tickers))
                f.close()
    print('completed: updating ', path)


def run_file_df_tickers(filepath):
    df = pd.read_csv(filepath)
    df = df.dropna()
    df = df[['Account Name', 'Symbol']]
    path = os.path.join(md.data_dir, 'holding')
    account_names = list(set(df['Account Name'].values))
    file_df_tickers(df, account_names, path)


if __name__ == '__main__':
    filepath = md.fidelity_positions_filep()
    run_file_df_tickers(filepath)