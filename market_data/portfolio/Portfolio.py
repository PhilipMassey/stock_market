
import market_data as md
import pandas as pd
from os.path import join
import gspread
from gspread_dataframe import get_as_dataframe# Authenticate with your Google account
gc = gspread.service_account(filename='/Users/philipmassey/.config/gspread/service_account.json')

class Portfolio:
    def __init__(self, workbook_name, portfolio):
        self.opsub = '-'
        self.opdiv = '/'
        self.openb = '('
        self.closeb = ')'
        self.opadd = '+'
        self.opmul = '*'
        self.workbook_name = workbook_name
        self.portfolio = portfolio
        self.sheet_id = md.dct_adjustment_id[self.portfolio]
        self.workbook = gc.open_by_url(md.dct_workbook_url[self.workbook_name])
        self.worksheet = self.workbook.get_worksheet_by_id(self.sheet_id)
        self.values = self.worksheet.get_all_values() # ` worksheet.get_all_values()
        # values = positions_df.values.tolist()
        self.column_names = self.values[0]
        self.col_char_dict = {column: chr(i + 65) for i, column in enumerate(self.column_names)}
        self.col_int_dict = {column: i + 1 for i, column in enumerate(self.column_names)}
        self.row_top = 2
        self.row_max = len(self.values)
        self.row_sum = self.row_max + 1

        self.dct_portfolio = {}
        self.dct_portfolio['Alpha Picks'] = md.dct_adjustment_id['Alpha Picks']
        self.dct_portfolio['Dividends'] = md.dct_adjustment_id['Dividends']
        self.dct_portfolio['ETFs'] = md.dct_adjustment_id['ETFs']
        self.dct_portfolio['Stocks'] = md.dct_adjustment_id['Stocks']
        self.dct_portfolio['International'] = md.dct_adjustment_id['International']
        self.dct_portfolio['Treasuries'] = md.dct_adjustment_id['Treasuries']

    def assign_columns_percent(self, colname_dest, colname_a, colname_b):
        cola = self.col_char_dict[colname_a]
        colb = self.col_char_dict[colname_b]
        row_idx = self.col_int_dict[colname_dest]
        # D =(C2-I2)/I2
        for i, row in enumerate(self.values):
            r = i + 2
            row[row_idx] = f'=({cola}{r}{self.opsub}{colb}{r}){self.opdiv}{colb}{r}'

    def append_row_sum_formulas(self):
        # ['Total','=SUM(B2:B731)', '=SUM(C2:C73)')
        row = ['Total']
        for col_name in self.column_names:
            col = self.col_char_dict[col_name]
            if col in self.sum_cols_chars:
                row.append(f'=SUM({col}{self.row_top}:{col}{self.row_max})')
            else:
                row.append('')
        values.append(row)

    def update_sheet_values(self):
        self.worksheet.update('A1', self.values, raw=False)

    def assign_columns_dollars(self, colname_dest, colname_a, colname_b):
        cola = self.col_char_dict[colname_a]
        colb = self.col_char_dict[colname_b]
        row_idx = self.col_int_dict[colname_dest]
        # D =(C2-I2)/I2
        for i, row in enumerate(self.values):
            r = i + 2
            row[row_idx] = f'=({cola}{r}{self.opsub}{colb}{r}){self.opmul}{colb}{r}'
