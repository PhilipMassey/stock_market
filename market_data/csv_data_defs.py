import pandas as pd
import os
from os.path import isfile, join, isdir
from os import listdir

import market_data as md

def portfolio_from_file(subdir,file):
    path = join(md.data_dir, subdir, file)
    df = pd.read_csv(path)
    fname = file[0:-4]
    df['portfolio'] = fname
    df.rename(columns={'Ticker':'symbol'},inplace=True)
    return df

def get_dir_port_symbols(subdir):
    path = os.path.join(md.data_dir, subdir)
    csv_files = [f for f in listdir(path) if isfile(join(path, f))]
    dfall = pd.DataFrame(columns=('portfolio', 'symbol'))
    for file in csv_files:
        dfall = pd.concat([dfall, portfolio_from_file(subdir, file)], axis=0)
    dfall.reset_index(drop=True, inplace=True)
    return dfall

def get_port_and_symbols(directory):
    df_all = pd.DataFrame(columns=('portfolio','symbol'))
    if directory is None or directory == md.all:
        dirs = [d for d in listdir(md.data_dir) if isdir(join(md.data_dir, d))]
        for dir in dirs:
            df = get_dir_port_symbols(dir)
            df_all = pd.concat([df_all, df], axis=0)
    else:
        df = get_dir_port_symbols(directory)
        df_all = pd.concat([df_all, df], axis=0)
    return df_all

def get_portfolios(directory):
    df_port = get_port_and_symbols(directory)
    return list(set(df_port.portfolio.values))

def get_symbols(directory='', ports=[]):
    if len(directory) > 0:
        df = get_port_and_symbols(directory)
        symbols = list(set(df.symbol.values))
    else:
        symbols = get_symbols_for_portfolios(ports)
    return symbols


def get_symbols_dir_and_port(directory, port):
    symbols = []
    if port == None or port == None:
        symbols = []
    elif len(port) == 0 or len(port) == 0:
        symbols = []
    else:
        df = md.get_port_and_symbols(directory)
        symbols = list(df[df.portfolio == port].symbol.values)
    return symbols


def get_symbols_dir_or_port(directory, port):
    symbols = []
    if port != None and len(port) > 0:
        symbols = md.get_symbols_for_portfolios([port])
    elif directory != None:
        df = md.get_port_and_symbols(directory)
        symbols = list(set(df.symbol.values))
    else:
        symbols = []
    return symbols

def get_symbols_for_portfolios(portfolios):
    port_symbols = md.get_port_and_symbols(md.all)
    return list(port_symbols[port_symbols['portfolio'].isin(portfolios)].symbol.values)


def get_ports_for_directory(directory):
    path = os.path.join(md.data_dir, directory)
    ports = [f for f in listdir(path) if isfile(join(path, f))]
    return [port[0:-4] for port in ports]


def get_directorys():
        return [d for d in listdir(md.data_dir) if isdir(join(md.data_dir, d))]


def symbols_from_file(fname):
    fo = open(fname, "r+")
    symbols = fo.read().split('\n')
    fo.close()
    return symbols[1:]


def getHighVolatilityStocks():
    path = '/Users/philipmassey/PycharmProjects/stock_market/market_data/data/volatile_stock.csv'
    df = pd.read_csv(path).set_index('symbol')
    symbols = list(df.index.values)
    return symbols

def getLowVolatilityStocks():
    path = '/Users/philipmassey/PycharmProjects/stock_market/market_data/data/low_vol_stocks.csv'
    df = pd.read_csv(path).set_index('symbol')
    symbols = list(df.index.values)
    return symbols

def getFidelitySymbols():
    path = '/Users/philipmassey/PycharmProjects/stock_market/market_data/data/fidelity.csv'
    df_fidelity = pd.read_csv(path).set_index('symbol')
    symbols = list(df_fidelity.index.values)
    return symbols



