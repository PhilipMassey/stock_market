---
description: Workflow mapping how CSV files in market_data are populated
---
# Populating CSVs in `market_data`

The `market_data` directory contains CSV files that keep track of stock symbols by portfolio, seeking alpha exports, and other exchange symbols. The process of populating these CSVs typically relies on files downloaded manually (or automatically) to the `/Users/philipmassey/Downloads/` directory and then processed through python scripts within the `stock_market/market_data` module.

## Workflow 1: Population of Fidelity Holding Portfolios (.csv) 
These CSV files are updated based on the `Portfolio_Positions[...].csv` exported from Fidelity.
They map your stock symbols to specific accounts ("Stocks", "Dividends", "ETFs", "Shorts", "International") and store them under `market_data/data/holding/`.

1. **Prerequisite**: Ensure that a Fidelity positions data export is downloaded to `/Users/philipmassey/Downloads/Portfolio_Positions*.csv`.
2. **Execution Steps**:
   Run the overarching update script which reads the CSV, cleans the data, renames and maps "Account Names", constructs CSV splits by account name, and updates your Market Database (MongoDB). 
   ```bash
   python3 /Users/philipmassey/stock_market/market_data/portfolio/holding_portfolios_update.py
   ```
   Alternatively, there is `read_fidexport_file_holding.py` which exclusively writes out the `.csv` account files if full aggregation is unwanted.

## Workflow 2: Population of Seeking Alpha Symbol Data (.xlsx -> .csv)
These CSV files are updated based on various Seeking Alpha `.xlsx` exports in your downloads directory. They extract just the necessary stock symbols and save them into `market_data/data/Seeking_Alpha/`.

1. **Prerequisite**: Ensure that your Seeking Alpha `.xlsx` exports are in `/Users/philipmassey/Downloads/`.
2. **Fix Malformed Excel Files**: Sometimes downloaded Excel sheets have corruption or malformed bytes. A JS script runs via Node.js to re-encode and save them properly.
   ```bash
   zsh "/Users/philipmassey/stock_market/market_data/scripts/run fix xlsx.zsh"
   ```
   *(This triggers `fix_xlsx.js`, reading from your `Downloads` directory and overwriting the fix in place.)*
3. **Execution Steps**: Now extract the symbols and convert them into CSV under the `market_data` directory structure.
   Run either:
   ```bash
   python3 /Users/philipmassey/stock_market/market_data/scripts/seeking_alpha_export.py
   ```
   or 
   ```bash
   python3 /Users/philipmassey/stock_market/market_data/xlsx_data/symbols_from_excel.py
   ```

## Workflow 3: Population of Exchange Symbols (xls -> csv)
If you have basic `.xlsx` files that simply need to be dumped row-to-row into `.csv` files into a target directory, the codebase also provides `xlsx_to_csv` function usage.
- File: `/Users/philipmassey/stock_market/market_data/exchange/xls_to_csv.py`
It executes data extraction and then backs up the processed `.xlsx` files so you don't run them twice.
