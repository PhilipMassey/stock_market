import market_data as md
import market_data as md
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe
gc = gspread.service_account(filename='/Users/philipmassey/.config/gspread/service_account.json')
from gspread_formatting import NumberFormat, batch_updater, cellFormat,format_cell_range,set_row_height,batch

dct_sum_cols_names = {md.portfolio_adjustments:['Buy/Sell $', 'Buy/Sell %','Current Value', 'Current Value %', 'Holding %', 'Cost Basis Total'],
                      md.portfolio_proforma:['Current Value','Cost Basis Total','Current Value %']}

dct_percent_cols_names = {md.portfolio_adjustments:['Current Return %'],
                          md.portfolio_proforma:['Current Return %']}

dct_percent_cols_formula = {md.portfolio_adjustments:{'Current Return %':['Current Value', 'Cost Basis Total']},
                            md.portfolio_proforma:{'Current Return %':['Current Value', 'Cost Basis Total']}}

dct_percent_total_names = {md.portfolio_adjustments:['Current Value %'],
                           md.portfolio_proforma:  ['Current Value %']}
dct_percent_total_formula = {md.portfolio_adjustments:{'Current Value %':'Current Value'},
                             md.portfolio_proforma:  {'Current Value %':'Current Value'}}

dct_currency_format_names = {md.portfolio_adjustments:['Buy/Sell $', 'Current Value', 'Cost Basis Total'],
                             md.portfolio_proforma:['Current Value','Cost Basis Total']}
dct_percent_format_names = {md.portfolio_adjustments:['Current Return %', 'Current Value %', 'Holding %','Buy/Sell %'],
                            md.portfolio_proforma:['Current Value %','Current Value %']}


currency_format =   cellFormat(
    numberFormat=NumberFormat(
        type='CURRENCY',
        pattern='$#,##0.00'),
    horizontalAlignment='RIGHT')

percent_format =   cellFormat(
    numberFormat=NumberFormat(
        type='PERCENT',
        pattern='0.00%'),
    horizontalAlignment='RIGHT')


class PortfolioCalculate:
    positions_df = None

    def __init__(self, workbook_name, portfolio_name):
        self.opsub = '-'
        self.opdiv = '/'
        self.openb = '('
        self.closeb = ')'
        self.opadd = '+'
        self.opmul = '*'
        self.workbook_name = workbook_name
        self.portfolio_name = portfolio_name
        self.sheet_id = md.dct_portfolio_dicts[self.workbook_name][self.portfolio_name]
        self.workbook = gc.open_by_url(md.dct_workbook_url[self.workbook_name])
        self.worksheet = self.workbook.get_worksheet_by_id(self.sheet_id)
        self.values = self.worksheet.get_all_values()  # ` worksheet.get_all_values()
        # values = positions_df.values.tolist()
        self.column_names = self.values[0]
        self.values = self.values[1:]
        self.col_char_dict = {column: chr(i + 65) for i, column in enumerate(self.column_names)}
        self.col_int_dict = {column: i + 1 for i, column in enumerate(self.column_names)}
        self.row_top = 2
        self.row_max = len(self.values) + 1
        self.row_sum = self.row_max + 1
        self.col_char_dict = {column: chr(i + 65) for i, column in enumerate(self.column_names)}
        self.col_int_dict = {column: i for i, column in enumerate(self.column_names)}

        self.sum_col_names = dct_sum_cols_names[self.workbook_name]
        self.sum_col_chars = [self.col_char_dict[col_name] for col_name in self.sum_col_names]
        self.sum_col_ints = [self.col_int_dict[col_name] for col_name in self.sum_col_names]

        self.percent_col_names = dct_percent_cols_names[self.workbook_name]
        self.percent_col_formula = dct_percent_cols_formula[self.workbook_name]
        self.percent_col_chars = [self.col_char_dict[col_name] for col_name in self.percent_col_names]

        self.percent_total_names = dct_percent_total_names[self.workbook_name]
        self.percent_total_formula = dct_percent_total_formula[self.workbook_name]

        # self.currency_format_names = dct_currency_format_names[self.workbook_name]
        # self.currency_col_chars = [self.col_char_dict[col_name] for col_name in self.currency_format_names]

        # self.percent_format_names = dct_currency_format_names[self.workbook_name]
        # self.percent_col_chars = [self.col_char_dict[col_name] for col_name in self.percent_format_names]

    def worksheet_update_with_values(self):
        self.worksheet.clear()
        values = self.values
        values.insert(0, self.column_names)
        self.worksheet.update('A1', values, raw=False)

    # replace_adjustments_sheet_with_values('Fidelity Positions','Fidelity Positions')

    def append_row_sum_formulas(self):
        # ['Total','=SUM(B2:B731)', '=SUM(C2:C73)')
        row = ['Total']
        for col_name in self.column_names[1:]:
            col = self.col_char_dict[col_name]
            if col in self.sum_col_chars:
                row.append(f'=SUM({col}{self.row_top}:{col}{self.row_max})')
            else:
                row.append('')
        self.values.append(row)

    def assign_columns_percent(self):
        # B4 = (B2-B3)/B3
        for colname_dest in self.percent_col_names:
            row_idx = self.col_int_dict[colname_dest]
            colname_a, colname_b = self.percent_col_formula[colname_dest]
            cola = self.col_char_dict[colname_a]
            colb = self.col_char_dict[colname_b]
            for i, row in enumerate(self.values):
                r = i + 2
                row[row_idx] = f'=({cola}{r}{self.opsub}{colb}{r}){self.opdiv}{colb}{r}'

    def assign_percent_of_total(self):
        # 'F2','C2'/'C33')
        for colname_dest in self.percent_total_names:
            row_idx = self.col_int_dict[colname_dest]
            colname_source = self.percent_total_formula[colname_dest]
            col_source = self.col_char_dict[colname_source]
            for i, row in enumerate(self.values):
                r = i + 2
                # print(row_idx, f'={col_source}{r}{opdiv}{col_source}{row_sum}')
                row[row_idx] = f'={col_source}{r}{self.opdiv}{col_source}{self.row_sum}'

    def assign_buysell_percent(colname_dest, colname_proforma, colname_current):
        row_idx = self.col_int_dict[colname_dest]
        col_pro = self.col_char_dict[colname_proforma]
        col_curr = self.col_char_dict[colname_current]
        opsub = '-'
        # 'H2','G2'-'F2')
        for i, row in enumerate(self.values):
            r = i + 2
            # print(row_idx, f'={col_pro}{r}{opsub}{col_curr}{r}')
            row[row_idx] = f'={col_pro}{r}{opsub}{col_curr}{r}'

    def assign_buysell_dollars(colname_dest, colname_perc, colname_current):
        row_idx = self.col_int_dict[colname_dest]
        col_per = self.col_char_dict[colname_perc]
        col_curr = self.col_char_dict[colname_current]
        opx = '*'
        # 'B2',=H2*C6
        for i, row in enumerate(self.values):
            r = i + 2
            # print(row_idx, f'={col_per}{r}{opx}{col_curr}{row_sum}')
            row[row_idx] = f'={col_per}{r}{opx}{col_curr}{row_sum}'


