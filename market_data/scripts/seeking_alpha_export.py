import os
from os.path import isfile, join
from os import listdir
import pylightxl as xl

import pandas as pd
import market_data as md

directory = '/Users/philipmassey/Downloads/'
xlsx_files = md.get_files_by_extension(directory, '.xlsx')

wpath = join(md.data_dir,md.sa)
for file_name in xlsx_files:
    file_path = join(directory,file_name)
    sheet_name = 'Summary'
    column_index = 1
    symbols = md.extract_symbols(file_path, sheet_name, column_index)
    cvs_filen = file_name.split('.')[0].rsplit(' ', 1)[0] + '.csv'
    md.write_to_csv(symbols,wpath,cvs_filen)