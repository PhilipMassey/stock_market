import requests

url = "https://seeking-alpha.p.rapidapi.com/screeners/get-results"

querystring = {"page":"1","per_page":"100"}
querystring = {"id":"95b89bfc0c"}

payload = "{\n    \"quant_rating\": {\n        \"gte\": 3.5,\n        \"lte\": 5\n    },\n    \"authors_rating_pro\": {\n        \"gte\": 3.5,\n        \"lte\": 5\n    },\n    \"sell_side_rating\": {\n        \"gte\": 3.5,\n        \"lte\": 5\n    },\n    \"value_category\": {\n        \"gte\": 1,\n        \"lte\": 6\n    },\n    \"growth_category\": {\n        \"gte\": 1,\n        \"lte\": 6\n    },\n    \"profitability_category\": {\n        \"gte\": 1,\n        \"lte\": 6\n    },\n    \"momentum_category\": {\n        \"gte\": 1,\n        \"lte\": 6\n    },\n    \"eps_revisions_category\": {\n        \"gte\": 1,\n        \"lte\": 6\n    }\n}"
headers = {
    'content-type': "application/json",
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': "b8e3f8e3c8msh1c3174e834acd9bp10bb99jsnba74a76fb55e"
    }

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

print(response.text)
data = response.json()['data']
import pandas as pd
df =pd.DataFrame.from_dict(data)
print(df['attributes'][0]['name'])