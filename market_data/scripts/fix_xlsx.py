import os
import pandas as pd

# Define the directory path
directory_path = os.path.expanduser('~/Downloads/')

# Iterate over each file in the directory
for file in os.listdir(directory_path):
    # Check if the file has an .xlsx extension
    if file.endswith('.xlsx'):
        file_path = os.path.join(directory_path, file)
        
        try:
            # Read all sheets using the 'calamine' engine which can handle invalid XML gracefully
            dfs = pd.read_excel(file_path, engine='calamine', sheet_name=None)
            
            # Save the workbook back, overwriting the original file using openpyxl (standard valid XML)
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet_name, df in dfs.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"File has been successfully fixed and overwritten: {file_path}")
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
