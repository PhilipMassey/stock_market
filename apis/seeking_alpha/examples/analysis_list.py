import requests

url = "https://seeking-alpha.p.rapidapi.com/analysis/v2/list"

querystring = {"id":"vt","until":"0","since":"0","size":"20","number":"1"}

headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': "b8e3f8e3c8msh1c3174e834acd9bp10bb99jsnba74a76fb55e"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)