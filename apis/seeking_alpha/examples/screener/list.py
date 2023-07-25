import requests
import market_data as md


url = "https://seeking-alpha.p.rapidapi.com/screeners/list"

headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': md.seeking_alpha_key
    }

response = requests.request("GET", url, headers=headers)

print(response.json())