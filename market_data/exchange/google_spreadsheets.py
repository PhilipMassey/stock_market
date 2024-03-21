import gspread
from gspread_dataframe import get_as_dataframe# Authenticate with your Google account
gc = gspread.service_account(filename='/Users/philipmassey/.config/gspread/service_account.json')


def df_from_google_spreadsheet(spreadsheet_url, sheet_id):
    spreadsheet = gc.open_by_url (spreadsheet_url)
    #print(spreadsheet.worksheets())
    sheet = spreadsheet.get_worksheet_by_id(2113142462)
    df = get_as_dataframe(sheet)
    return df

def worksheet_update_with_df(spreadsheet_url, sheet_id, df):
    spreadsheet = gc.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.get_worksheet_by_id(sheet_id)
    worksheet.clear()
    data = df.values.tolist()
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