import market_data as md
import apis
from pprint import pprint
from datetime import datetime
from pymongo import MongoClient
client = MongoClient()
db = client[md.db_client]

#db_coll = db[md.db_volume]

# DROP COLUMN
def drop_column(col_name,db_coll_name):
    #col_name = 'AMZN'
    db_coll = db[db_coll_name]
    print('total documents',db_coll.count_documents({col_name:{'$gte':0}}))
    result = db_coll.update_many( {col_name:{'$gte':0}}, { '$unset': { col_name: '' } } )
    print(result.matched_count, result.modified_count)

# UPDATE DATE
def update_date(dt,newdt, db_coll_name):
    db_coll = db[db_coll_name]
    print('total documents',db_coll.count_documents({'Date':{'$eq':dt}}))
    myquery = { "Date": dt }
    newvalues = { "$set": { "Date": newdt} }
    result = db_coll.update_many(myquery, newvalues)
    print(result.matched_count, result.modified_count)

def df_symbols_no_profile():
    symbols = md.get_symbols(md.all)
    df = apis.df_symbol_profile(symbols=symbols, fields=['sectorname', 'primaryname', 'symbol'])
    # df[df.sectorname.notna()]
    return df[df.sectorname.isna()]

def update_rows_sectprim(rows):
    db_coll_name = md.db_symbol_profile
    db_coll = db[db_coll_name]
    for row in rows:
        symbol = row[2]
        sectorname = row[0]
        primaryname = row[1]
        one = db_coll.find_one({'symbol': symbol})
        print(one['symbol'], one['sectorname'], one['primaryname'])
        query = {'symbol': {'$eq': symbol}}
        newvalues = {"$set": {'sectorname': sectorname, 'primaryname': primaryname}}
        result = db_coll.update_one(query, newvalues)
        one = db_coll.find_one({'symbol': symbol})
        print(one['symbol'], one['sectorname'], one['primaryname'])
