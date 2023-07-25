import requests
import pandas as pd
import json
from json import JSONDecodeError
import os
import market_data as md
subdir = 'Seeking_Alpha'
suffix = '.csv'


def get_sa_screener_details_list():
    url = "https://seeking-alpha.p.rapidapi.com/screeners/list"

    headers = {
        'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
        'x-rapidapi-key': md.seeking_alpha_key
    }

    response = requests.request("GET", url, headers=headers)

    response.text
    datas = json.loads(response.text)['data']
    alist = []
    for data in datas:
        name = data['attributes']['name']
        flter = data['attributes']['filters']
        alist.append((name, str(flter).replace("'", '"')))
    return alist

def adict_screener_details(screeners, perpage):
    url = "https://seeking-alpha.p.rapidapi.com/screeners/get-results"
    headers = {
        'content-type': "application/json",
        'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
        'x-rapidapi-key': md.seeking_alpha_key
    }
    querystring = {"page": "1", "per_page": "" + str(perpage) + ""}

    adict = {}
    error_count = 0
    for screener in screeners:
        try:
            print(screener[0],end=', ')
            fname = screener[0]
            payload = screener[1].replace(', "disabled": False','').replace('"authors_rating_pro"','"authors_rating"')
            response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
            data = response.text
            if str(data) == '400 - Bad Request' or 'error' in str(data):
                print(data)
                print(screener[0], screener[1])
            else:
                df = pd.json_normalize(json.loads(data)['data'])
                tickers = df['attributes.name'].values
                adict[fname] = list(tickers)
        except (JSONDecodeError,KeyError) as e:
            print('\n',e, fname)
            error_count += 1
    return adict


def write_screener_parameters():
    screeners = apis.get_sa_screener_details_list()
    home = '/Users/philipmassey/'
    subdir = 'Downloads/Investing/rapidapi/seeking alpha'
    fname = 'Screener details'
    suffix = '.json'
    path = os.path.join(home,subdir,fname +suffix)
    with open(path, 'w') as f:
        for idx in range(len(screeners)):
            screener = screeners[idx]
            f.write(screener[0] + '\n')
            f.write(screener[1])
    f.close()

