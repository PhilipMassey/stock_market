import market_data as md
import numpy as np
import os
import pytz
from datetime import datetime

def run_mdb_missing(symbols, ndays_from, ndays_to):
    load_missing_failed = []
    for ndays in range(ndays_to,  ndays_from):
        failed_count_before = len(load_missing_failed)
        symbols = md.update_mdb_with_missing_row(ndays, symbols, load_missing_failed)
        
        newly_failed = load_missing_failed[failed_count_before:]
        if newly_failed:
            print(f"Failed this run: {newly_failed}")
            for el in newly_failed:
                if el in symbols:
                    symbols.remove(el)
        else:
            print("OK")
    values, counts = np.unique(load_missing_failed, return_counts=True)
    print(values, counts)

def get_ndays_previous_busday():
    # find the previous day in NYSE
    # return the previous business day
    # Calculate the exact dates based on New York Time
    ny_now = datetime.now(pytz.timezone('America/New_York'))
    nbus_days_now = md.get_nbusdays_from_date(ny_now)
    ndays_start = md.get_nbusdays_from_date(to_date)
    return 1

def get_year_bdays_from():
    ny_now = datetime.now(pytz.timezone('America/New_York'))
    from_date = ny_now - relativedelta(years=1)
    ndays_from = md.get_nbusdays_from_date(from_date)
    return ndays_from


if __name__ == '__main__':
    ndays_to = 1
    ndays_from = get_year_bdays_from()

    incl = md.all
    symbols = md.get_symbols(incl)
    run_mdb_missing(symbols, ndays_from, ndays_to)