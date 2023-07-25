import http.client

conn = http.client.HTTPSConnection("seeking-alpha.p.rapidapi.com")

headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': "b8e3f8e3c8msh1c3174e834acd9bp10bb99jsnba74a76fb55e"
    }

conn.request("GET", "/v2/auto-complete?query=apple&type=people%2Csymbols%2Cpages&size=5", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))

