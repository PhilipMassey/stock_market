import requests
import pandas as pd
import json
import os
from os.path import join
import market_data as md
import apis as apis
perpage = 60

def change_value_to_list(dictionary):
    for key in dictionary:
        dictionary[key] = list(dictionary[key])


def get_china_symbols():
    base = '/Users/philipmassey/PycharmProjects/stock_market'
    subdir = 'logs'
    fname= 'china.csv'
    path = join(base, subdir, fname)
    df = pd.read_csv(path)
    df.rename(columns={'Ticker':'symbol'},inplace=True)
    return list(set(df.symbol.values))


def remove_elements(alist, elements):
    for el in elements:
        if el in alist:
            alist.remove(el)


def remove_china_stocks(resultsdict):
    csymbols = get_china_symbols()
    for port in resultsdict.keys():
        remove_elements(resultsdict[port], csymbols)
    print('remove china stocks')


def trim_to_count(resultsdict, dict_count):
    for port in resultsdict.keys():
        trim = dict_count[port]
        resultsdict[port] = resultsdict[port][:trim]
    print('trimmed resultsdict')


def replacedot(resultsdict):
    for port in resultsdict:
        listtickers = resultsdict[port]
        newtickers = []
        for ticker in listtickers:
            newtickers.append(ticker.replace(".",'-'))
        resultsdict[port] = newtickers


def file_api_symbols(resultsdict, path):
    suffix = '.csv'
    for key in resultsdict.keys():
        tickers = resultsdict[key]
        fpath = os.path.join(path, key + suffix)
        with open(fpath, 'w') as f:
            f.write('Ticker\n' + '\n'.join(tickers))
            f.close()
    print('completed: updating ', path)

def filter_to_sector_screeners(screeners):
    nscreeners = []
    for screener in screeners:
        if screener[0] in md.sa_sectors:
            nscreeners.append(screener)
    return nscreeners
