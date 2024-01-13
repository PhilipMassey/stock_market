import market_data as md
import pandas as pd
import apis
import analysis

def tuple_count_sum_mean(ndays_range, symbols):
    for ndays in reversed(ndays_range):
        if md.check_mdb_on_date(ndays,md.db_close):
            break;
    df_last = md.get_df_from_mdb_for_nday(ndays,md.db_close,symbols)
    ndays = ndays_range[0]
    df_first = md.get_df_from_mdb_for_nday(ndays,md.db_close,symbols)
    df = pd.concat([df_first, df_last], ignore_index=False)
    percent_change = df.pct_change()
    last_row_count = percent_change.iloc[-1].count()
    last_row_sum = percent_change.iloc[-1].sum()
    last_row_mean = percent_change.iloc[-1].mean()
    return (last_row_count, round(last_row_sum*100,2), round(last_row_mean*100,2))

def assign_count_sum_mean(df, ndays_range):
    counts = []
    totals = []
    means = []
    for index, row in df.iterrows():
        # Retrieve the values for each row except the first column
        values_except_first_column = row[1:]
        symbols = [x for x in values_except_first_column if x is not None]
        tuple_csm = tuple_count_sum_mean(ndays_range, symbols)
        counts.append(tuple_csm[0])
        totals.append(tuple_csm[1])
        means.append(tuple_csm[2])
    df['Count'] = counts
    df['Total %'] = totals
    df['Mean %'] = means