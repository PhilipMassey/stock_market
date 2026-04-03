import os
import requests
import json

url = "https://seeking-alpha.p.rapidapi.com/symbols/get-top-holdings"

querystring = {"symbol":"schd"}
querystring = {"symbol":"ftcs"}

headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': os.environ.get("RAPID_API_KEY")
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(dict(json.loads(response.text)['data'][0]['attributes'])['list'])
