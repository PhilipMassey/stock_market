import asyncio
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from notebooklm import NotebookLMClient

# 1. Setup GSpread Authentication
SERVICE_ACCOUNT_FILE = '/Users/philipmassey/.config/gspread/service_account.json'
SPREADSHEET_ID = '1seOmQCJ_xKVYv0RZN3UMjJO330z94dpzN6BSm48T3Vg'

async def main():
    print("Connecting to NotebookLM...")
    try:
        # 2. Fetch Notebooks from NotebookLM
        async with await NotebookLMClient.from_storage() as client:
            notebooks = await client.notebooks.list()
            
            if not notebooks:
                print("No notebooks found.")
                return

            # Prepare data for the spreadsheet
            data = [{"Title": nb.title, "ID": nb.id} for nb in notebooks]
            df = pd.DataFrame(data)

            # 3. Update the Google Sheet
            print(f"Connecting to Google Sheet: {SPREADSHEET_ID}...")
            gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
            sh = gc.open_by_key(SPREADSHEET_ID)
            worksheet = sh.get_worksheet(0) # Targeting gid=0

            set_with_dataframe(worksheet, df)
            print(f"Success! Updated sheet with {len(df)} notebooks.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # This is the standard way to run async code in a .py script
    asyncio.run(main())
