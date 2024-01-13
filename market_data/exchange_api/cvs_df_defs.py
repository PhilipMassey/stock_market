import os

import pandas as pd


def df_from_cvs(filepath,column_names):
    df = pd.read_csv(filepath)
    df = df[column_names]
    df.dropna(axis=0, how='all', inplace=True)
    return df


def df_sum_column(df, column_name='Current Value'):
    return df[column_name].sum()


def df_symbol_sum(df, column_name):
    # Force all non-numeric values to NaN and convert the remaining values to integers
    df[column_name] = df[column_name].fillna(0).astype(float)
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    grouped_df = df.groupby([column_name ])[column_name].sum().reset_index()
    return grouped_df

def get_files_by_extension(directory, extension):
    files = []
    for file in os.listdir(directory):
        if file.endswith(extension):
            files.append(file)
    return files

def write_df_to_file(df, file_path):
    output_string = df.to_string(index=False)
    with open(file_path, 'w') as f:
        f.write(output_string)

