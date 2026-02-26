---
description: Weekly workflow to process Fidelity Investments Portfolio Positions
---
# Weekly Fidelity Portfolio Update Flow

This workflow maps out the weekly process of updating portfolio data using the exported CSV from Fidelity Investments. 

## 1. Download Data
*   **Action**: Download the exported `Portfolio_Positions[...date...].csv` file from Fidelity Investments.
*   **Destination**: Save this file in your `/Users/philipmassey/Downloads/` directory.

## 2. Process Holdings and Update Core Systems
Run the `holding_portfolios_update.py` script to process the downloaded CSV. This script performs four key actions:
1.  **Google Sheets Update**: Updates the `'Fidelity Positions'` worksheet in the `'Portfolio Adjustments'` Google Sheets workbook.
2.  **CSV Files Update**: Updates the CSV files in `market_data/data/holding` (`md.data_dir + 'Holding'`) with the current portfolio positions per account.
3.  **Money Market File Creation**: Extracts current portfolio cash (Money Market funds) and saves it to a file (e.g., `Money Market.txt`).
4.  **MongoDB Update**: Inserts the aggregated Fidelity positions into the MongoDB collection (`md.db_fidel_pos`), keyed by the date parsed from the downloaded `Portfolio_Positions[...date...].csv` filename.

```bash
python3 /Users/philipmassey/stock_market/market_data/portfolio/holding_portfolios_update.py
```

## 3. Update Portfolio Adjustments Worksheets
After the main data has been processed, run the `update_adjustment_with_fidelity.py` script. 
*   **Action**: This script calculates the percentages and updates the individual portfolio worksheets in the `'Portfolio Adjustments'` Google workbook.
*   **Data Updated**: For each portfolio worksheet, it updates the `Symbol`, `Current Value %`, and `Current Return %`.

```bash
python3 /Users/philipmassey/stock_market/market_data/portfolio/update_adjustment_with_fidelity.py
```
