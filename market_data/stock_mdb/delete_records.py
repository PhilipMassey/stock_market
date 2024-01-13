import market_data as md
from datetime import datetime
import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client['stock_market']

# delete all
# results = db[db_coll_name].delete_many({})
# results.deleted_count

def drop_column(db_coll_name, col_name):
    db_coll = db[db_coll_name]
    result = collection.update_many( { }, { '$unset': { col_name: '' } } )
    print(result.matched_count, result.modified_count)


def delete_row_for_day(ndays, db_coll_name):
    adate = md.get_date_for_mdb(ndays)
    db_coll = db[db_coll_name]
    result = db_coll.delete_one({'Date': adate})
    return result.deleted_count


def count_and_delete_for_day(ndays,db_coll_name):
    db_coll = db[db_coll_name]
    df = md.get_df_from_mdb_for_nday(ndays, db_coll_name)
    print(df)
    adate = md.get_date_for_mdb(ndays)
    adate
    result = db_coll.delete_many({'Date': adate})
    return result.deleted_count

def delete_records_between_dates(ndays,perdiod, db_coll_name):
    start_date, end_date = md.get_ndate_and_todate(ndays,period)
    start_date, end_date = md.get_mdbdate_from_strdate(start_date),md.get_mdbdate_from_strdate(end_date)
    db_coll = db[db_coll_name]
    result = db_coll.delete_many({'Date': {'$lte': end_date, '$gte': start_date}})
    return result.deleted_count

def delete_records_for_row(symbols, db_coll_name):
    db_coll = db[db_coll_name]
    result = db_coll.delete_many({"row_name": {"$in": symbols}})
    return result.deleted_count

def delete_all_records(symbols, db_coll_name):
    db_coll = db[db_coll_name]
    result = db_coll.delete_many({})
    return result.deleted_count