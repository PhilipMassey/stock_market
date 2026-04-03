import os
import requests

url = "https://seeking-alpha.p.rapidapi.com/analysis/v2/list"

querystring = {"id":"vt","until":"0","since":"0","size":"20","number":"1"}

headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': os.environ.get("RAPID_API_KEY")
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)