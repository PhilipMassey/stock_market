import market_data as md

incl = md.all
start = md.get_ndays_for_end()
end = 260

def run_mdb_missing_old(symbols):
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


def run_mdb_missing(symbols):
    load_missing_failed = []
    for ndays in range(start, end):
        symbols = md.update_mdb_with_missing_row(ndays, symbols, load_missing_failed)
        print(load_missing_failed)
        for el in load_missing_failed:
            if el in symbols:
                symbols.remove(el)
        print()
    # print('Content md.load_missing_failed',md.load_missing_failed)
    #import numpy as np
    #values, counts = np.unique(load_missing_failed, return_counts=True)
    #print(values, counts)

if __name__ == '__main__':
    incl = md.all
    start = md.get_ndays_for_end()
    start = 1
    end = 260
    symbols = md.get_symbols(incl)
    run_mdb_missing(symbols)