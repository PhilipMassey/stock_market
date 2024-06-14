# import market_data as md
# import pandas as pd
# from os.path import join
# import gspread
# from gspread_dataframe import get_as_dataframe# Authenticate with your Google account
# gc = gspread.service_account(filename='/Users/philipmassey/.config/gspread/service_account.json')
#
#
#
# positions_df =md.df_from_google_spreadsheet(md.portfolio_proforma,md.dct_proforma_id['Fidelity Positions'])
#
# portfolios = ['Alpha Picks', 'Dividends', 'ETFs', 'Stocks','International', 'Treasuries']
# portfolio = portfolios[2]
# print(portfolio)
# proforma_df = md.df_from_google_spreadsheet(md.portfolio_proforma, md.dct_proforma_id[portfolio])
# filtered_df = positions_df[positions_df['Symbol'].isin(proforma_df.Symbol)]
# merged_df = pd.merge(filtered_df[['Symbol','Current Value','Cost Basis Total']], proforma_df, on='Symbol', how='inner')
# df = merged_df
# df['Buy/Sell %'] = 0
# df['Buy/Sell $'] = 0
# df['Current Value %'] = 0
# df['Current Value %'] = 0
# df['Current Return %'] = 0
# df = df[['Symbol', 'Buy/Sell $', 'Current Value', 'Current Return %', 'Rating', 'Current Value %',
#                              'Holding %', 'Buy/Sell %', 'Cost Basis Total']]
# values = df.values.tolist()
# headers = df.columns.tolist()
# #worksheet.clear()
#
# row_max = len(values) + 1
# col_max = len(values[0])
# row_sum = row_max + 1
#
# col_char_dict = {column: chr(i + 65) for i, column in enumerate(headers)}
# col_int_dict = {column: i for i, column in enumerate(headers)}
# sum_cols_names = ['Buy/Sell $', 'Buy/Sell %','Current Value', 'Current Value %', 'Holding %', 'Cost Basis Total']
# sum_cols_chars = [col_char_dict[col_name] for col_name in sum_cols_names]
# currency_col_names = ['Current Value', 'Cost Basis Total',  'Buy/Sell $']
# currency_col_chars = [col_char_dict[col_name] for col_name in currency_col_names]
# percent_col_names = ['Current Return %', 'Current Value %', 'Holding %', 'Buy/Sell %']
# percent_col_chars = [col_char_dict[col_name] for col_name in percent_col_names]


# In[120]:

#
# append_row_sum_formulas()
#assign_columns_percent('Current Return %', 'Current Value', 'Cost Basis Total' )
# assign_percent_of_total('Current Value %' ,'Current Value')
# assign_buysell_percent('Buy/Sell %', 'Holding %', 'Current Value %')
# assign_buysell_dollars('Buy/Sell $' ,'Buy/Sell %','Current Value')


# In[121]:


# values.insert(0, headers)
# workbook = gc.open_by_url(md.dct_workbook_url['Portfolio Adjustments'])
# worksheet = workbook.get_worksheet_by_id(md.dct_adjustment_id[portfolio])
# worksheet.update('A1', values, raw=False)

#replace_adjustments_sheet_with_values('Fidelity Positions','Fidelity Positions')


def append_row_sum_formulas():
    # ['Total','=SUM(B2:B731)', '=SUM(C2:C73)')
    row_top = 2
    row = ['ZTotal']
    for col_name in headers[1:]:
        col = col_char_dict[col_name]
        if col in sum_cols_chars:
            row.append(f'=SUM({col}{row_top}:{col}{row_max})')
        else:
            row.append('')
    values.append(row)


# def assign_columns_percent(colname_dest,colname_a,colname_b):
#     cola = col_char_dict[colname_a]
#     colb = col_char_dict[colname_b]
#     row_idx = col_int_dict[colname_dest]
#     opsub = '-'
#     opdiv = '/'
#     openb = '('
#     closeb = ')'
#     # D  =(C2-I2)/I2
#     for i, row in enumerate(values):
#         r = i +2
#         row[row_idx] = f'=({cola}{r}{opsub}{colb}{r}){opdiv}{colb}{r}'


# def assign_percent_of_total(colname_dest, colname_source):
#     col_source = col_char_dict[colname_source]
#     row_idx = col_int_dict[colname_dest]
#     opdiv = '/'
#     # 'F2','C2'/'C33')
#     for i, row in enumerate(values):
#         r = i+2
#         #print(row_idx, f'={col_source}{r}{opdiv}{col_source}{row_sum}')
#         row[row_idx] = f'={col_source}{r}{opdiv}{col_source}{row_sum}'


def assign_buysell_percent(colname_dest, colname_proforma, colname_current):
    row_idx = col_int_dict[colname_dest]
    col_pro = col_char_dict[colname_proforma]
    col_curr = col_char_dict[colname_current]
    opsub = '-'
    # 'H2','G2'-'F2')
    for i, row in enumerate(values):
        r = i+2
        #print(row_idx, f'={col_pro}{r}{opsub}{col_curr}{r}')
        row[row_idx] = f'={col_pro}{r}{opsub}{col_curr}{r}'


def assign_buysell_dollars(colname_dest, colname_perc, colname_current):
    row_idx = col_int_dict[colname_dest]
    col_per = col_char_dict[colname_perc]
    col_curr = col_char_dict[colname_current]
    opx = '*'
    # 'B2',=H2*C6
    for i, row in enumerate(values):
        r = i+2
        #print(row_idx, f'={col_per}{r}{opx}{col_curr}{row_sum}')
        row[row_idx] = f'={col_per}{r}{opx}{col_curr}{row_sum}'


# def replace_adjustments_sheet_with_values(sheet, replace_sheet):
#     spreadsheet = 'Portfolio Adjustments'
#     workbook = gc.open_by_url(md.dct_workbook_url[spreadsheet])
#     worksheet = workbook.get_worksheet_by_id(md.dct_adjustment_id[sheet])
#     values = worksheet.get_all_values()
#     vdf = pd.DataFrame(values[1:],columns=['Symbol', 'Buy/Sell $', 'Current Value', 'Current Return %', 'Rating', 'Current Value %',
#                                  'Holding %', 'Buy/Sell %', 'Cost Basis Total'])
#     vdf.head(2)
#     values
#     worksheet = workbook.get_worksheet_by_id(md.dct_adjustment_id[replace_sheet])
#     worksheet.update('A1', values)
#     print('Replaced with values: ', spreadsheet, sheet, replace_sheet)




