import os
import requests

url = "https://seeking-alpha.p.rapidapi.com/screener-filters/list"

headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': os.environ.get("RAPID_API_KEY")
    }

response = requests.request("GET", url, headers=headers)

print(response.text)