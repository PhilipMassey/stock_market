import os
import requests

url = "https://seeking-alpha.p.rapidapi.com/screeners/detail"

querystring = {"id":"95b89bfc0c"}

headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': os.environ.get("RAPID_API_KEY")
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)