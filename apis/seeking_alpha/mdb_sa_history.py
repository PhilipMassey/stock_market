
import requests
import pandas as pd
import market_data as md
from pymongo import MongoClient
client = MongoClient()
db = client['stock_market']

def df_seeking_alpha_ports(ndays=0):
    df = md.get_dir_port_symbols('Seeking_Alpha')
    print(df.shape[0],'\tsymbols in Seeking Alpha')
    strdt = md.get_mdb_strdate_for_ndays(ndays)
    dt = md.get_mdbdate_from_strdate(strdt)
    df['Date'] = dt
    df.set_index('Date', inplace=True)
    return df


def sa_into_mdb(df, db_coll_name):
    results = md.add_df_to_db(df, db_coll_name, dropidx=False)
    print(len(results.inserted_ids), '\tCount of updates added to ',db_coll_name)


def mdb_sa_history():
    print('running mdb_sa_history')
    db_coll_name = md.db_seeking_alpha_history
    df = df_seeking_alpha_ports()
    sa_into_mdb(df, db_coll_name)

if __name__ == '__main__':
    mdb_sa_history()