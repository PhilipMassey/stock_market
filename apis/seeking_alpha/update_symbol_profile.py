"""
Populate MongoDB md.db_symbol_profile from RapidAPI Seeking Alpha (get-profile).

- Source: RapidAPI Seeking Alpha, GET /symbols/get-profile?symbols=...
- Target: MongoDB collection symbol_profile (md.db_symbol_profile).
- Behaviour: Insert only. Symbols that already have a profile are skipped; no updates.
- Reporting: Only sectorname (Sector) and primaryname (Industry) are used,
  for reports that group by Sector and Industry. We store only those fields (+ symbol, Date).

Weekly refresh (feasibility / subscription testing):
- symbol_profile_cache: raw API response per symbol + last_updated.
- refresh_symbol_profile_cache(): call API for all portfolio symbols, upsert cache; reports API call count.
- sync_profile_cache_to_symbol_profile(): copy cache -> symbol_profile so reporting unchanged.
"""
import json
import http.client
import time
from datetime import datetime

import pandas as pd
import market_data as md
from market_data.stock_mdb.mongo_connection_manager import get_mongo_database

# Only these are used for reports (Sector / Industry grouping)
PROFILE_REPORT_FIELDS = ["symbol", "sectorname", "primaryname"]

conn = http.client.HTTPSConnection("seeking-alpha.p.rapidapi.com")
headers = {
    "x-rapidapi-host": "seeking-alpha.p.rapidapi.com",
    "x-rapidapi-key": md.seeking_alpha_key,
}


def dct_api_symbol_profile(symbols):
    dct_symbol_profile = {}
    for idx in range(0,len(symbols),4):
        symbols4= "%2C".join(symbols[idx:idx+4])

        conn.request("GET", "/symbols/get-profile?symbols=" + symbols4, headers=headers)

        res = conn.getresponse()
        data = res.read()
        txt = data.decode("utf-8")
        if 'data' not in txt:
            print('No data ',symbols)
            continue
        ldcts = json.loads(txt)['data']
        for idx in range(len(ldcts)):
            dct_symbol_profile[ldcts[idx]['id']] = ldcts[idx]['attributes']

    return dct_symbol_profile


def refresh_symbol_profile_cache(delay_seconds=0.5):
    """
    Fetch Seeking Alpha profile for all portfolio symbols and upsert into symbol_profile_cache.
    Use for weekly refresh; prints API call count to gauge RapidAPI subscription need.
    """
    db = get_mongo_database("stock_market")
    cache_coll = db[md.db_symbol_profile_cache]
    dirs = md.get_directorys()
    all_symbols = set()
    for directory in dirs:
        ports = md.get_ports_for_directory(directory)
        for port in ports:
            all_symbols.update(md.get_symbols(ports=[port]))
    symbols = sorted(all_symbols)
    if not symbols:
        print("refresh_symbol_profile_cache: no symbols, skip")
        return 0
    n_calls = (len(symbols) + 3) // 4
    print("refresh_symbol_profile_cache: %d symbols -> %d API calls (RapidAPI)" % (len(symbols), n_calls))
    for idx in range(0, len(symbols), 4):
        batch = symbols[idx : idx + 4]
        dct_api = dct_api_symbol_profile(batch)
        for sym, attrs in dct_api.items():
            doc = {"symbol": sym, **attrs, "last_updated": datetime.utcnow()}
            cache_coll.replace_one({"symbol": sym}, doc, upsert=True)
        if delay_seconds > 0 and idx + 4 < len(symbols):
            time.sleep(delay_seconds)
    print("refresh_symbol_profile_cache: done, %d symbols in %s" % (len(symbols), md.db_symbol_profile_cache))
    return n_calls


def sync_profile_cache_to_symbol_profile():
    """Copy symbol_profile_cache -> symbol_profile (sectorname, primaryname) so reports use latest cache."""
    db = get_mongo_database("stock_market")
    cache_coll = db[md.db_symbol_profile_cache]
    profile_coll = db[md.db_symbol_profile]
    cursor = cache_coll.find({}, {"symbol": 1, "sectorname": 1, "primaryname": 1})
    ndays = 0
    date_val = md.get_date_for_mdb(ndays)
    count = 0
    for doc in cursor:
        symbol = doc.get("symbol")
        if not symbol:
            continue
        update_doc = {
            "symbol": symbol,
            "sectorname": doc.get("sectorname"),
            "primaryname": doc.get("primaryname"),
            "Date": date_val,
        }
        profile_coll.replace_one({"symbol": symbol}, update_doc, upsert=True)
        count += 1
    print("sync_profile_cache_to_symbol_profile: %d rows -> %s" % (count, md.db_symbol_profile))


def mdb_add_symbols_profiles_for_directory(ndays, directory, db_coll_name):
    """Insert profile for symbols not yet in DB (insert only; no updates)."""
    ports = md.get_ports_for_directory(directory)
    mdb_symbols = md.mdb_profile_get_symbols()
    for port in ports:
        print("\t", port, end=": ")
        symbols = md.get_symbols(ports=[port])
        not_added_symbols = set(symbols).difference(set(mdb_symbols))
        print(len(not_added_symbols))
        if len(not_added_symbols) == 0:
            continue
        print("\t\t no profile: ", not_added_symbols)
        dct_api = dct_api_symbol_profile(list(not_added_symbols))
        if len(dct_api) == 0:
            continue
        df = pd.DataFrame.from_dict(dct_api)
        df = df.T.reset_index().rename(columns={"index": "symbol"})
        # Store only fields used for reports (Sector / Industry)
        cols = [c for c in PROFILE_REPORT_FIELDS if c in df.columns]
        df = df[cols].copy()
        md.df_add_ndays_date_column(ndays, df)
        md.mdb_add_df(df, db_coll_name)
        mdb_symbols.extend(not_added_symbols)

def update_symbol_profile():
    """Insert new symbols only (RapidAPI Seeking Alpha -> symbol_profile). No updates to existing profiles."""
    print("update_symbol_profile: insert new symbols only (RapidAPI Seeking Alpha -> symbol_profile)")
    dirs = md.get_directorys()
    ndays = 0
    db_coll_name = md.db_symbol_profile
    for directory in dirs:
        print("Directory:", directory)
        mdb_add_symbols_profiles_for_directory(ndays, directory, db_coll_name)

def check_no_profile(symbols):
    df = md.df_symbols_no_profile(symbols)
    print('No profile: ',df.size / 3)
    input1 = 'Sector Equity'
    input2 = 'Blend'
    for val in df[df.sectorname.isna()]['symbol'].values:
        result = [input1, input2, val]
        print(result)

def fill_in_profile():
    rows = [
        ['Sector Equity', 'Blend', 'VEU']
    ]
    md.update_rows_sectprim(rows)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "refresh":
        # Weekly refresh: API -> symbol_profile_cache, then sync -> symbol_profile (reports API call count)
        refresh_symbol_profile_cache(delay_seconds=0.5)
        sync_profile_cache_to_symbol_profile()
    else:
        update_symbol_profile()
    # symbols = md.get_symbols(md.all)
    # directory = 'Holding'
    # symbols = md.get_symbols_dir_or_port(directory, None)
    # check_no_profile(symbols)
    # fill_in_profile()