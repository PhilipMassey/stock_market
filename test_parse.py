import pandas as pd
import os

file_path = "/Users/philipmassey/Downloads/a check 2026-04-12.xlsx"
try:
    print("Trying calamine engine...")
    df = pd.read_excel(file_path, engine="calamine")
    df.to_excel("temp.xlsx", index=False)
    print("Success with calamine!")
except Exception as e:
    print("Calamine failed:", e)

