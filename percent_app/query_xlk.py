import pandas as pd
from pymongo import MongoClient
import market_data as md

try:
    client = MongoClient()
    db = client[md.db_client]
    collection = db[md.db_fidel_pos]

    unique_dates = sorted(collection.distinct("Date"), reverse=True)
    print("Unique dates:", unique_dates[:15])

    data = []
    for d in unique_dates[:20]:
        docs = list(collection.find({"Date": d, "Symbol": "XLK"}))
        for doc in docs:
            data.append({
                "Date": d,
                "Symbol": doc.get("Symbol"),
                "Current Value": doc.get("Current Value"),
                "Quantity": doc.get("Quantity", 0)
            })

    df = pd.DataFrame(data)
    if not df.empty:
        df['Price'] = df['Current Value'] / df['Quantity']
        print(df)
    else:
        print("No XLK data found.")
except Exception as e:
    print("Error:", e)
