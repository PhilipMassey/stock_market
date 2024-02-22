from os.path import join
import pandas as pd


def xlswriter_xlsxfile_from_df(df, directory, xlsxfilename):
    filep = join(directory, xlsxfilename)
    writer = pd.ExcelWriter(filep, engine="xlsxwriter" )
    df.to_excel(writer, sheet_name='Sheet1')
    return writer


def df_from_xlsxfile(directory, xlsxfilename):
    filep = join(directory,  xlsxfilename)
    df = pd.read_excel(filep)
    # for i,column in enumerate(df.columns):
    #     print(column,i,end=',')
    # print('/n')
    return df

def close_writer(writer):
    writer.close()

def dfs_compare_symbols(df1, df2):
    symbols1 = set(df1.Symbol.values)
    symbols2= set(df2.Symbol.values)
    print('Symbols1; ',symbols1.difference(symbols2))
    print('Symbols2: ',symbols2.difference(symbols1))
    print('Shapes: ',df1.shape,df2.shape)
