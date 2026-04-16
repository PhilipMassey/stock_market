import os
import openpyxl

# Define the directory path
directory_path = os.path.expanduser('~/Downloads/')

# Iterate over each file in the directory
for file in os.listdir(directory_path):
    # Check if the file has an .xlsx extension
    if file.endswith('.xlsx'):
        file_path = os.path.join(directory_path, file)
        
        try:
            # Read the Excel file
            workbook = openpyxl.load_workbook(file_path)
            
            # Save the workbook, overwriting the original file
            # This fixes formatting warnings when opened in Excel
            workbook.save(file_path)
            
            print(f"File has been overwritten: {file_path}")
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
