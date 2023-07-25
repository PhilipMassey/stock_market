import requests
import xmltodict
import pandas as pd

def df_fidelity_sectors():
    url = "https://fidelity-investments.p.rapidapi.com/market/get-sectors"
    headers = {
        'x-rapidapi-host': "fidelity-investments.p.rapidapi.com",
        'x-rapidapi-key': monthly
        }

    response = requests.request("GET", url, headers=headers)
    adict = xmltodict.parse(response.text)
    df = pd.DataFrame.from_dict(adict['Chart']['Symbol'])
    return df

df = df_fidelity_sectors()
print(df)