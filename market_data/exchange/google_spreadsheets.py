import market_data as md
import gspread
from gspread_dataframe import get_as_dataframe# Authenticate with your Google account
gc = gspread.service_account(filename='/Users/philipmassey/.config/gspread/service_account.json')


def df_from_google_spreadsheet(spreadsheet, sheet_id, evaluate_formulas=True):
    workbook = gc.open_by_url(md.dct_sheet_url[spreadsheet])
    worksheet = workbook.get_worksheet_by_id(sheet_id)
    df = get_as_dataframe(worksheet, evaluate_formulas=evaluate_formulas)
    df = df.drop(columns=df.columns[df.columns.str.contains('Unnamed')])
    df = df.dropna()
    return df

def get_worksheet_symbols(spreadsheet,sheet_id):
    df = df_from_google_spreadsheet(spreadsheet,sheet_id)
    return df.Symbol.values


def worksheet_update_with_df(workbook_name, worksheet_id, df):
    workbook_url = md.dct_sheet_url[workbook_name]
    workbook = gc.open_by_url(workbook_url)
    worksheet = workbook.get_worksheet_by_id(worksheet_id)
    worksheet.clear()
    data = df.values.tolist()
    headers = df.columns.tolist()
    data.insert(0, headers)
    worksheet.update('A1', data)
    print('updated worksheet', worksheet)

def df_google_alpha_picks_standard():
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1bTsH3cjQDGR-Mlnq-bypRqhGIHJApKKJgsgXWSemur4/edit#gid=2113142462'
    #print(spreadsheet.worksheets())
    worksheetid = 2113142462
    df = df_from_google_spreadsheet(spreadsheet_url, worksheetid)
    df = df.drop(columns=df.columns[df.columns.str.contains('Unnamed')])
    df = df.dropna()
    df = df.groupby('Symbol').agg(
        {'Holding %': 'sum', 'Sector': 'first', 'Rating': 'first', 'Company': 'first', 'Picked': 'first',
         'Return': 'first'}).reset_index()
    return df