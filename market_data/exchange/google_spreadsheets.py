import market_data as md
import gspread
from gspread_dataframe import get_as_dataframe# Authenticate with your Google account
gc = gspread.service_account(filename='/Users/philipmassey/.config/gspread/service_account.json')


def df_from_google_spreadsheet(workbook_name, sheet_id, evaluate_formulas=True):
    workbook = gc.open_by_url(md.dct_workbook_url[workbook_name])
    worksheet = workbook.get_worksheet_by_id(sheet_id)
    df = get_as_dataframe(worksheet, evaluate_formulas=evaluate_formulas)
    df = df.drop(columns=df.columns[df.columns.str.contains('Unnamed')])
    df = df.dropna()
    return df

def get_worksheet_symbols(spreadsheet,sheet_id):
    df = df_from_google_spreadsheet(spreadsheet,sheet_id)
    return df.Symbol.values


def worksheet_update_with_df_old(workbook_name, worksheet_id, df):
    workbook_url = md.dct_workbook_url[workbook_name]
    workbook = gc.open_by_url(workbook_url)
    worksheet = workbook.get_worksheet_by_id(worksheet_id)
    worksheet.clear()
    data = df.values.tolist()
    headers = df.columns.tolist()
    data.insert(0, headers)
    result = worksheet.update('A1', data)
    print('\tupdated', worksheet)
    return result

def worksheet_update_with_df(workbook_name, worksheet_id, df):
    workbook_url = md.dct_workbook_url[workbook_name]
    workbook = gc.open_by_url(workbook_url)
    worksheet = workbook.get_worksheet_by_id(worksheet_id)
    # If you need to clear old data that might be longer than the new DataFrame,
    # use batch_clear() with a range. This clears VALUES but keeps FORMATTING.
    worksheet.batch_clear(["A1:Z119"])
    # Use set_with_dataframe to update values only.
    # It preserves existing formatting (colors, fonts, borders).
    result = set_with_dataframe(worksheet, df, row=1, col=1, include_index=False, include_column_header=True)
    print('\tupdated', worksheet, '\t',result)

def worksheet_get_all_values(workbook_name, sheet_id):
    workbook = gc.open_by_url(md.dct_workbook_url[workbook_name])
    worksheet = workbook.get_worksheet_by_id(sheet_id)
    return  worksheet.get_all_values()

def replace_worksheet_with_values(worksheet):
    values = worksheet.get_all_values()
    worksheet.update('A1', values)
    print('Replaced with values: ', worksheet)
