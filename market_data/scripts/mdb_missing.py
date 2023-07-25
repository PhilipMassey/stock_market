import sys
sys.path.extend(['/Users/philipmassey/PycharmProjects/stock_market'])
sys.path.extend(['/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages'])
import market_data as md

incl = md.all
start = md.get_ndays_for_end()
end = 260

def run_mdb_missing(symbols):
    load_missing_failed = []
    for ndays in range(start, end):
        symbols = md.update_mdb_with_missing_row(ndays, symbols, load_missing_failed)
        for el in load_missing_failed:
            if el in symbols:
                symbols.remove(el)
        print()
    #print('Content md.load_missing_failed',md.load_missing_failed)
    import numpy as np
    values, counts = np.unique(load_missing_failed, return_counts=True)
    print(values, counts)
        # [md.update_mdb_with_missing_row(ndays, directory) for ndays in range(start, end)]

if __name__ == '__main__':
    symbols = md.get_symbols(incl)
    run_mdb_missing(symbols)