import market_data as md
import numpy as np
incl = md.all
start = md.get_ndays_for_end()
end = 260


def run_mdb_missing(symbols):
    load_missing_failed = []
    for ndays in range(start, end):
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


if __name__ == '__main__':
    incl = md.all
    start = md.get_ndays_for_end()
    start = 1
    end = 260
    symbols = md.get_symbols(incl)
    run_mdb_missing(symbols)