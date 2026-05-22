import pandas as pd
from datetime import datetime, timedelta
import market_data as md
from market_data.stock_mdb.mongo_connection_manager import get_mongo_database
import argparse

def get_daily_change(symbols, weeks_ago=0):
    """
    Query the FidelityPositionsDaily collection to calculate and display
    the daily change in Current Value and the total for the defined period.
    """
    print(f"Calculating daily change for {weeks_ago} weeks ago for {symbols}...\n")
    
    # 1. Connect to MongoDB
    db = get_mongo_database(md.db_client)
    
    # Ensure backwards compatibility if md.db_fidel_pos_daily isn't strictly set yet
    daily_coll_name = getattr(md, 'db_fidel_pos_daily', 'FidelityPositionsDaily')
    daily_coll = db[daily_coll_name]

    schedule = md.get_schedule()
    if len(schedule) == 0:
        print("Schedule is empty.")
        return pd.DataFrame()
        
    s = pd.Series(schedule)
    weeks = s.dt.isocalendar().year.astype(str) + '-' + s.dt.isocalendar().week.astype(str).str.zfill(2)
    unique_weeks = weeks.drop_duplicates().tolist()
    unique_weeks.reverse() # index 0 is current week
    
    if weeks_ago >= len(unique_weeks):
        print(f"No schedule data available for {weeks_ago} weeks ago.")
        return pd.DataFrame()
        
    target_week = unique_weeks[weeks_ago]
    week_indices = s.index[weeks == target_week].tolist()
    
    start_idx = week_indices[0]
    end_idx = week_indices[-1]
    
    # Include the previous business day so we can compute diff() for the first day of the week
    if start_idx > 0:
        start_idx -= 1
        
    target_dates = schedule[start_idx:end_idx+1]
    
    start_date = target_dates[0].replace(tzinfo=None)
    end_date = target_dates[-1].replace(tzinfo=None)

    # 2. Query the data
    query = {
        "Symbol": {"$in": symbols},
        "Date": {"$gte": start_date, "$lte": end_date}
    }
    cursor = daily_coll.find(query, {'_id': 0})
    df = pd.DataFrame(list(cursor))

    if not df.empty:
        # 3. Pivot the data to get Dates as rows and Symbols as columns
        df_pivot = df.pivot(index='Date', columns='Symbol', values='Current Value')
        
        # 4. Calculate the day-to-day difference and drop the first row (which will be NaN)
        df_diff = df_pivot.diff().dropna()
        
        # Format the Date index to only show YYYY-MM-DD
        df_diff.index = df_diff.index.strftime('%Y-%m-%d')
        
        # 5. Add the Total row across all dates in this period
        df_diff.loc['Total'] = df_diff.sum()
        
        # 6. Format as currency for terminal display
        def format_currency(val):
            if pd.isna(val): return ""
            return f"${val:,.2f}" if val >= 0 else f"-${abs(val):,.2f}"
            
        # Using applymap for pandas <= 2.0.0, or map for newer versions
        if hasattr(df_diff, 'map'):
            df_formatted = df_diff.map(format_currency)
        else:
            df_formatted = df_diff.applymap(format_currency)
            
        print(df_formatted.to_string())
        return df_formatted
    else:
        print("No data found for the selected symbols in the given period.")
        return pd.DataFrame()

if __name__ == "__main__":
    weeks_ago = 1 
    symbols = md.get_symbols_dir_and_port('Holding','Stocks')
    get_daily_change(symbols, weeks_ago=weeks_ago)
