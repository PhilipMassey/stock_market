
from pymongo import MongoClient
client = MongoClient()
db = client['stock_market']


client = MongoClient("mongodb+srv://bolsa:HV7x8ZEr3SDSQwfr@cluster0.x7v1g.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.test
print(db)