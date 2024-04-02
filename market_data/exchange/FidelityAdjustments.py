import warnings
warnings.filterwarnings('ignore')
import pandas as pd
from os.path import join
import market_data as md

class CombineHoldingsStandards:
    def __init__(self,standards_xlsxfilen, postition_xlsxfilen):
        standards_directory = join(md.download_dir, 'Fidelity','Portfolio Standards')
        self.df_standard = md.df_from_xlsxfile(standards_directory, standards_xlsxfilen)
        #self.df_standard = md.df_google_alpha_picks_standard()
        positions_directory = join(md.download_dir, 'Fidelity','Fidelity Positions')
        self.df_fidelity = md.df_from_xlsxfile(positions_directory, postition_xlsxfilen)

    def prepare_df_fidelity(self):
        self.df_fidelity.drop(columns=['Unnamed: 0'],inplace=True)
        #md.dfs_compare_symbols(self.df_standard, self.df_fidelity)
        columns = ['Holding %', 'Rating']
        md.df_copy_columns_values(self.df_fidelity,self.df_standard, columns)


class AdjustmentFromHoldingsStandards:
    def __init__(self, df):
        self.df = df
        self.col_char_dict = {column: chr(i + 66) for i, column in enumerate(df.columns)}
        self.sum_cols_names = ['Buy/Sell $', 'Current Value', 'Current Value %', 'Holding %', 'Cost Basis Total']
        self.sum_cols_chars = [self.col_char_dict[col_name] for col_name in self.sum_cols_names]
        currency_col_names = ['Current Value', 'Cost Basis Total', 'Average Cost Basis', 'Buy/Sell $']
        self.currency_col_chars = [self.col_char_dict[col_name] for col_name in currency_col_names]
        percent_col_names = ['Current Return %', 'Current Value %', 'Holding %', 'Buy/Sell %']
        self.percent_col_chars = [self.col_char_dict[col_name] for col_name in percent_col_names]
        self.worksheet = None
        self.workbook = None
        self.worksheet = None
        self.row_max = None
        self.row_end = None

    def create_excel_writer(self, directory, xlsxfilename):
        self.directory = join(md.download_dir, 'Fidelity', 'Fidelity Adjustments')
        self.xlsxfilename = xlsxfilename
        self.writer = md.xlswriter_xlsxfile_from_df(self.df, self.directory, self.xlsxfilename)
        self.worksheet = self.writer.sheets['Sheet1']
        self.workbook = self.writer.book

    def write_totals_row(self):
        self.row_max = self.worksheet.dim_rowmax + 2
        self.row_end = self.row_max - 1
        self.worksheet.write_row(self.row_max - 1, 1, 'T')

    def write_col_formula(self, op, cols):
        col_dest = cols[0]
        col_left = cols[1]
        col_right = cols[2]
        cola = self.col_char_dict[col_dest]
        colb = self.col_char_dict[col_left]
        colc = self.col_char_dict[col_right]
        row_max = self.row_max
        # worksheet.write_formula('A2','B2'+'C2')
        for row in range(2, row_max):
            self.worksheet.write_formula(f'{cola}{row}', f'{colb}{row}{op}{colc}{row}')

    def write_sum_formulas(self):
        # worksheet.write_formula('D32','=SUM(D2:D31)')
        for col in self.sum_cols_chars:
            self.worksheet.write_formula(f'{col}{self.row_max}', f'=SUM({col}2:{col}{self.row_end})')

    def write_current_return_percent(self):
        col_dest = self.col_char_dict['Current Return %']
        cola = self.col_char_dict['Current Value']
        colb = self.col_char_dict['Cost Basis Total']
        # E3,(D3−J3)÷J3
        opsub = '-'
        opdiv = '/'
        openb = '('
        closeb = ')'
        for row in range(2, self.row_max):
            self.worksheet.write_formula(f'{col_dest}{row}',
                                         f'{openb}{cola}{row}{opsub}{colb}{row}{closeb}{opdiv}{colb}{row}')

    def write_current_value_percent(self):
        col_dest = self.col_char_dict['Current Value %']
        colcurr = self.col_char_dict['Current Value']
        row_max = self.row_max
        row_end = self.row_end
        opdiv = '/'
        # G4, D4÷D$33
        for row in range(2, self.row_end):
            self.worksheet.write_formula(f'{col_dest}{row}', f'{colcurr}{row}{opdiv}{colcurr}{row_max}')

    def write_buy_sell_dollar(self):
        col_dest = self.col_char_dict['Buy/Sell $']
        colcurr = self.col_char_dict['Buy/Sell %']
        colsum = self.col_char_dict['Current Value']
        row_max = self.row_max
        row_end = self.row_end
        opdiv = '*'
        # G4, D4÷D$33
        for row in range(2, self.row_max):
            self.worksheet.write_formula(f'{col_dest}{row}', f'{colcurr}{row}{opdiv}{colsum}{row_max}')

    def format_sheet(self):
        workbook = self.workbook
        worksheet = self.worksheet
        bold_format = workbook.add_format({'bold': True})
        money_format = workbook.add_format({'num_format': '$#,##0.00'})
        percent_format = workbook.add_format({'num_format': '#,##0.00%'})
        date_format = workbook.add_format({'num_format': 'MM-dd-yyyy'})

        self.worksheet.default_col_width = 15
        # worksheet.set_column(1, 1, 15)
        for format in workbook.formats:
            format.set_font_name('Arial')
            format.set_font_size(12)
        worksheet.default_date_format = {'num_format': 'MM-dd-yyyy'}
        for col in self.currency_col_chars:
            worksheet.set_column(f'{col}:{col}', None, money_format)
        for col in self.percent_col_chars:
            worksheet.set_column(f'{col}:{col}', None, percent_format)

            # worksheet.autofit()

    def complete_xlsx_adjust(self):
        md.close_writer(self.writer)
        print('Completed: ', self.directory, self.xlsxfilename)

