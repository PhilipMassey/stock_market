
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



# curl --request GET \
# 	--url 'https://seeking-alpha.p.rapidapi.com/symbols/get-meta-data?symbol=aapl' \
# 	--header 'x-rapidapi-host: seeking-alpha.p.rapidapi.com' \
# 	--header 'x-rapidapi-key: b8e3f8e3c8msh1c3174e834acd9bp10bb99jsnba74a76fb55e'

def df_api_symbol_id(symbol):
    req = "/symbols/get-meta-data?symbol="+symbol
    conn.request("GET", req, headers=headers)
    res = conn.getresponse()
    data = res.read()
    txt = data.decode("utf-8")

    return json.loads(txt)

symbols = ['GOOGL']

dct = df_api_symbol_id(symbols[0])
print(dct['data']['id'])
#df = pd.DataFrame.from_dict(dct)
#print(df)