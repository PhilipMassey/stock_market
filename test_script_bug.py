import market_data as md
import pandas as pd
from market_data.stock_mdb.mongo_connection_manager import get_mongo_database
from datetime import datetime

db = get_mongo_database(md.db_client)
daily_coll_name = getattr(md, 'db_fidel_pos_daily', 'FidelityPositionsDaily')
daily_coll = db[daily_coll_name]

schedule = md.get_schedule()
s = pd.Series(schedule)
weeks = s.dt.isocalendar().year.astype(str) + '-' + s.dt.isocalendar().week.astype(str).str.zfill(2)
unique_weeks = weeks.drop_duplicates().tolist()
unique_weeks.reverse()
target_week = unique_weeks[0]
week_indices = s.index[weeks == target_week].tolist()
start_idx = week_indices[0]
end_idx = week_indices[-1]
if start_idx > 0: start_idx -= 1
target_dates = schedule[start_idx:end_idx+1]
start_date = target_dates[0].replace(tzinfo=None)
end_date = target_dates[-1].replace(tzinfo=None)
print("start_date:", start_date, "end_date:", end_date)

symbols = md.get_symbols_dir_and_port('Holding','Stocks')
query = {
    "Symbol": {"$in": symbols},
    "Date": {"$gte": start_date, "$lte": end_date}
}
cursor = daily_coll.find(query, {'_id': 0})
df = pd.DataFrame(list(cursor))
print("DF IS EMPTY:", df.empty)
