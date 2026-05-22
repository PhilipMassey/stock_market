import pandas as pd
from pymongo import MongoClient, ReplaceOne
import market_data as md
from market_data.stock_mdb.mongo_connection_manager import get_mongo_database
import time

def update_daily_fidelity_positions():
    db = get_mongo_database(md.db_client)
    fidel_coll = db[md.db_fidel_pos]
    close_coll = db[md.db_close]
    
    daily_coll_name = getattr(md, 'db_fidel_pos_daily', 'FidelityPositionsDaily')
    daily_coll = db[daily_coll_name]

    print("Fetching dates...")
    unique_close_dates = sorted(close_coll.distinct("Date"))
    unique_fidel_dates = sorted(fidel_coll.distinct("Date"))

    if not unique_fidel_dates:
        print("No fidelity dates found in database.")
        return

    min_fidel_date = unique_fidel_dates[0]
    valid_close_dates = [d for d in unique_close_dates if d >= min_fidel_date]
    
    print(f"Processing {len(valid_close_dates)} business days since {min_fidel_date.strftime('%Y-%m-%d')}...")

    total_inserted = 0

    for close_date in valid_close_dates:
        # Find the most recent fidel_date <= close_date
        le_fidel_dates = [d for d in unique_fidel_dates if d <= close_date]
        if not le_fidel_dates:
            continue
        fidel_date = le_fidel_dates[-1]
        
        # Get quantities from the most recent fidelity upload
        fidel_data = fidel_coll.find({"Date": fidel_date})
        df_quantities = pd.DataFrame(list(fidel_data))
        if df_quantities.empty or 'Quantity' not in df_quantities.columns:
            continue
        
        df_quantities = df_quantities[['Symbol', 'Quantity']].set_index('Symbol')
        
        # Get close prices for the business date
        close_doc = close_coll.find_one({"Date": close_date})
        if not close_doc:
            continue
        
        ps_prices = pd.Series({k:v for k,v in close_doc.items() if k not in ['_id', 'Date', 'index']})
        
        # Intersect to get symbols that exist in both
        common = df_quantities.index.intersection(ps_prices.index)
        if common.empty:
            continue
            
        df_daily = pd.DataFrame(index=common)
        df_daily['Symbol'] = common
        df_daily['Date'] = close_date
        df_daily['Quantity'] = df_quantities.loc[common]['Quantity']
        df_daily['Close Price'] = ps_prices.loc[common]
        df_daily['Current Value'] = df_daily['Quantity'] * df_daily['Close Price']
        
        # Insert into daily collection
        records = df_daily.to_dict('records')
        
        # Use bulk write with ReplaceOne to avoid duplicates (upsert based on Date and Symbol)
        operations = [
            ReplaceOne(
                {"Date": record["Date"], "Symbol": record["Symbol"]},
                record,
                upsert=True
            ) for record in records
        ]
        
        if operations:
            result = daily_coll.bulk_write(operations)
            total_inserted += result.upserted_count + result.modified_count

    print(f"Successfully processed {len(valid_close_dates)} dates. Updated/Inserted {total_inserted} daily positions.")

if __name__ == '__main__':
    start = time.time()
    update_daily_fidelity_positions()
    print(f"Completed in {time.time() - start:.2f} seconds.")

