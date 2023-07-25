import requests
import pandas as pd
import json
import os
import market_data as md

import market_data

url = "https://seeking-alpha.p.rapidapi.com/screeners/get-results"

querystring = {"page":"1","per_page":"20"}
payload = "{\n    \"quant_rating\": {\n        \"gte\": 3.5,\n        \"lte\": 5\n    },\n    \"authors_rating_pro\": {\n        \"gte\": 3.5,\n        \"lte\": 5\n    },\n    \"sell_side_rating\": {\n        \"gte\": 3.5,\n        \"lte\": 5\n    },\n    \"value_category\": {\n        \"gte\": 1,\n        \"lte\": 6\n    },\n    \"growth_category\": {\n        \"gte\": 1,\n        \"lte\": 6\n    },\n    \"profitability_category\": {\n        \"gte\": 1,\n        \"lte\": 6\n    },\n    \"momentum_category\": {\n        \"gte\": 1,\n        \"lte\": 6\n    },\n    \"eps_revisions_category\": {\n        \"gte\": 1,\n        \"lte\": 6\n    }\n}"
payload = '{"quant_rating": {"gte": 3.5, "lte": 5.0}, "authors_rating_pro": {"gte": 3.5, "lte": 5.0},"sell_side_rating": {"gte": 3.5, "lte": 5.0},"value_category": {"gte": 1, "lte": 6.0},"growth_category": {"gte": 1, "lte": 6.0},"profitability_category": {"gte": 1, "lte": 6.0},"momentum_category": {"gte": 1, "lte": 6.0},"eps_revisions_category": {"gte": 1, "lte": 6.0}}'
payload = '{"quant_rating": {"gte": 3.5, "lte": 5.0}, "authors_rating_pro": {"gte": 3.5, "lte": 5.0}, "sell_side_rating": {"gte": 3.5, "lte": 5.0}, "value_category": {"gte": 1, "lte": 6.0}, "growth_category": {"gte": 1, "lte": 6.0}, "profitability_category": {"gte": 1, "lte": 6.0}, "momentum_category": {"gte": 1, "lte": 6.0}, "eps_revisions_category": {"gte": 1, "lte": 6.0}}'
fname = 'get-results'
headers = {
    'content-type': "application/json",
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': "b8e3f8e3c8msh1c3174e834acd9bp10bb99jsnba74a76fb55e"
    }

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
#print(response.text)
data = response.text
print(data)
df = pd.json_normalize(json.loads(data)['data'])
tickers = df['attributes.name'].head(12).values
print(tickers)
subdir = 'Seeking_Alpha'
suffix = '.csv'
path = os.path.join(md.data_dir, subdir,fname+suffix)
with open(path, 'w') as f:
    f.write('Ticker\n'+'\n'.join(tickers))
    f.close()

