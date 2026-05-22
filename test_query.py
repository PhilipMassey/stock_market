import market_data as md
from market_data.stock_mdb.mongo_connection_manager import get_mongo_database
from datetime import datetime, timedelta

db = get_mongo_database(md.db_client)
daily_coll = db['FidelityPositionsDaily']

schedule = md.get_schedule()
days_back = 400
target_dates = schedule[-(days_back + 1):]
start_date = target_dates[0].replace(tzinfo=None)
end_date = target_dates[-1].replace(tzinfo=None)

query = {
    "Symbol": {"$in": ["AAPL"]},
    "Date": {"$gte": start_date, "$lte": end_date}
}
print(query)
cursor = daily_coll.find(query, {'_id': 0})
print(len(list(cursor)))
