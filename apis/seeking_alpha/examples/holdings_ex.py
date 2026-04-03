import os
import requests

url = "https://seeking-alpha.p.rapidapi.com/symbols/get-holdings"

querystring = {"symbols":"ftcs"}

headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': os.environ.get("RAPID_API_KEY")
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)