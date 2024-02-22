import requests
import pandas as pd
import json
import os
from os.path import join
import market_data as md
import apis as apis
perpage = 30

def change_value_to_list(dictionary):
    for key in dictionary:
        dictionary[key] = list(dictionary[key])


def get_china_symbols():
    base = md.data_dir
    fname= 'china.csv'
    path = join(base, fname)
    df = pd.read_csv(path)
    df.rename(columns={'Symbol':'symbol'},inplace=True)
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
        listsymbols = resultsdict[port]
        newsymbols = []
        for symbol in listsymbols:
            newsymbols.append(symbol.replace(".",'-'))
        resultsdict[port] = newsymbols


def file_api_symbols(resultsdict, path):
    suffix = '.csv'
    for key in resultsdict.keys():
        symbols = resultsdict[key]
        fpath = os.path.join(path, key + suffix)
        with open(fpath, 'w') as f:
            f.write('Symbol\n' + '\n'.join(symbols))
            f.close()
    print('completed: updating ', path)

def filter_to_sector_screeners(screeners):
    nscreeners = []
    for screener in screeners:
        if screener[0] in md.sa_sectors:
            nscreeners.append(screener)
    return nscreeners

def filter_to_top_screeners(screeners):
    nscreeners = []
    for screener in screeners:
        if screener[0] in md.sa_top_screeners:
            nscreeners.append(screener)
    return nscreeners
