import requests
import json
import http.client
import market_data as md
import pandas as pd
import apis as ra_apis
conn = http.client.HTTPSConnection("seeking-alpha.p.rapidapi.com")

headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': md.seeking_alpha_key
    }

#./symbols/get-earnings?ticker_ids=1567&period_type=annual&relative_periods=-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11&estimates_data_items=revenue_actual,revenue_consensus_low,revenue_consensus_mean,revenue_consensus_high,revenue_num_of_estimates
#
#
def dct_api_symbol_earings():
    req = "/symbols/get-earnings?ticker_ids=148893&period_type=annual&relative_periods=-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11&estimates_data_items=revenue_actual,revenue_consensus_low,revenue_consensus_mean,revenue_consensus_high,revenue_num_of_estimates"

    conn.request("GET", req, headers=headers)

    res = conn.getresponse()
    data = res.read()
    txt = data.decode("utf-8")

    return json.loads(txt)

symbols = ['AAPL']

dct = dct_api_symbol_earings()
print(dct)
df = pd.DataFrame.from_dict(dct)
print(df)