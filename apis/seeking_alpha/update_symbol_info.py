import market_data as md
import apis
from json import JSONDecodeError

def mdb_add_symbol_info_for_symbols(ndays, period, symbols,db_coll_name):
    total_symbols = len(symbols)
    update_count = 0
    skipped = 0
    error_count = 0
    for symbol in symbols:
        try:
            count = md.count_mdb_symbol_detween_dates(ndays, period, symbol, db_coll_name)
            if count == 0:
                print('+', end='')
                df = apis.df_symbol_info(ndays, symbol)
                apis.add_symbol_info_mdb(ndays, period, symbol, df, db_coll_name)
                update_count += 1
            else:
                skipped += 1
                print('>', end='')
        except (JSONDecodeError,KeyError) as e:
            print('\n',e, symbol)
            error_count += 1

    print('\nOf',total_symbols, '+', update_count, '>',skipped)
    if error_count > 0:
        print('errors',error_count)

def update_symbol_info():
    print('running update_symbol_profile')
    directories = md.get_directorys()
    db_coll_name = md.db_symbol_info
    ndays = 0
    period = 10
    for directory in directories:
        print(directory)
        symbols = md.get_symbols(directory)
        mdb_add_symbol_info_for_symbols(ndays, period, symbols,db_coll_name)


if __name__ == '__main__':
    update_symbol_info()