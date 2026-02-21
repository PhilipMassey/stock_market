# Weekly update: company data → CSVs

Scripts update **symbol-keyed company information** and write results to CSV files for use elsewhere.

## What runs (in order)

1. **Screener update** (optional) – Fetches Seeking Alpha screener results and overwrites symbol-list CSVs under `SM_DATA_DIR/Seeking_Alpha/` (e.g. `Top Rated Stocks.csv`, `Stocks by Quant.csv`).
2. **Symbol profile** – For symbols in your portfolio directories, fetches company profile from Seeking Alpha (sector, name, market cap, ratios, etc.) and stores in MongoDB `symbol_profile`.  
   - Default: **insert only** (new symbols); no updates.  
   - With `--profile-refresh`: re-fetches **all** portfolio symbols into MongoDB `symbol_profile_cache`, then syncs to `symbol_profile`. Use this to test how many API calls a weekly full refresh needs (for RapidAPI subscription planning).
3. **Symbol info** – Fetches key data/summary per symbol and stores in MongoDB `symbol_info`.
4. **SA portfolio history** – Writes current Seeking Alpha portfolio symbol lists with a date to MongoDB `db_seeking_alpha_history`.
5. **Export to CSV** – Reads latest record per symbol from MongoDB and writes:
   - `SM_DATA_DIR/company_data/symbol_profile.csv`
   - `SM_DATA_DIR/company_data/symbol_info.csv`
   - `SM_DATA_DIR/company_data/company_info.csv` (merged profile + info)

All company CSVs are keyed by **symbol** (one row per ticker).

## Environment variables

| Variable | Required | Purpose |
|----------|----------|--------|
| `SEEKING_ALPHA_KEY` | Yes | RapidAPI key for `seeking-alpha.p.rapidapi.com` |
| `SM_DATA_DIR` | Yes | Root data directory (portfolio CSVs live here; `company_data/` is created under it) |
| `DOWNLOAD_DIR` | No | Used by some portfolio/paths (e.g. Fidelity exports) |

MongoDB is used for profile and info; ensure it is running and that your app connects to the `stock_market` database.

## Run manually

From the **repository root** (so that `apis` and `market_data` are importable):

```bash
# Full weekly run (screener → profile → info → history → export)
python -m apis.seeking_alpha.weekly_update

# Only refresh screener symbol lists
python -m apis.seeking_alpha.weekly_update --screener-only

# Skip screener and CSV export (e.g. only refresh MongoDB)
python -m apis.seeking_alpha.weekly_update --no-screener --no-export

# Only export existing MongoDB data to CSV (no API calls)
python -m apis.seeking_alpha.weekly_update --no-screener --no-profile --no-info --no-sa-history

# Weekly profile refresh: re-fetch all portfolio symbols from API into symbol_profile_cache, then sync to symbol_profile (reports API call count to gauge RapidAPI subscription)
python -m apis.seeking_alpha.weekly_update --profile-refresh
```

## Schedule weekly (cron)

Example: run every Sunday at 8 PM. Edit crontab with `crontab -e`:

```cron
0 20 * * 0 SEEKING_ALPHA_KEY=your_key SM_DATA_DIR=/path/to/data DOWNLOAD_DIR=/path/to/downloads python -m apis.seeking_alpha.weekly_update >> /path/to/logs/weekly_update.log 2>&1
```

Use the same Python/environment you use for the rest of the project (e.g. activate your venv in the cron line or wrap in a small shell script that sets env and runs the command).

## Schedule weekly (macOS launchd)

1. Create a plist, e.g. `~/Library/LaunchAgents/com.stockmarket.weekly_update.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.stockmarket.weekly_update</string>
  <key>ProgramArguments</key>
  <array>
    <string>/path/to/venv/bin/python</string>
    <string>-m</string>
    <string>apis.seeking_alpha.weekly_update</string>
  </array>
  <key>WorkingDirectory</key>
  <string>/Users/you/stock_market</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>SEEKING_ALPHA_KEY</key>
    <string>your_key</string>
    <key>SM_DATA_DIR</key>
    <string>/path/to/data</string>
  </dict>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key>
    <integer>0</integer>
    <key>Hour</key>
    <integer>20</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>/path/to/logs/weekly_update.log</string>
  <key>StandardErrorPath</key>
  <string>/path/to/logs/weekly_update_err.log</string>
</dict>
</plist>
```

2. Load and start:

```bash
launchctl load ~/Library/LaunchAgents/com.stockmarket.weekly_update.plist
```

## Customizing exported CSV columns

Edit `apis/seeking_alpha/export_symbol_data_to_csv.py`:

- `PROFILE_CSV_COLUMNS` – columns for `symbol_profile.csv`
- `INFO_CSV_COLUMNS` – columns for `symbol_info.csv`
- `COMPANY_CSV_SUBDIR` – subdirectory under `SM_DATA_DIR` (default `company_data`)

Pass `columns=None` to the export functions to write all available columns.
