import os
import requests

url = "https://seeking-alpha.p.rapidapi.com/v2/auto-complete"

querystring = {"query":"apple","type":"people,symbols,pages","size":"5"}

headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': os.environ.get("RAPID_API_KEY")
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)