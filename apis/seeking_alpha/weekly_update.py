"""
Weekly runner: update symbol list CSVs, fetch company data from Seeking Alpha,
store in MongoDB, then export company data to CSV files.

Schedule with cron or launchd (e.g. every Sunday evening).

Required env:
  SEEKING_ALPHA_KEY   - RapidAPI key for seeking-alpha.p.rapidapi.com
  SM_DATA_DIR         - Data root (portfolio CSVs and company_data output)
  DOWNLOAD_DIR        - Optional; used by some portfolio paths

Usage:
  python -m apis.seeking_alpha.weekly_update
  python -m apis.seeking_alpha.weekly_update --no-screener --no-export
"""
import argparse
import sys
from datetime import datetime

import market_data as md

# Use apis package so screener + api_update helpers resolve
import apis
from apis.seeking_alpha.update_symbol_profile import (
    update_symbol_profile,
    refresh_symbol_profile_cache,
    sync_profile_cache_to_symbol_profile,
)
from apis.seeking_alpha.update_symbol_info import update_symbol_info
from apis.seeking_alpha.export_symbol_data_to_csv import run_export
from apis.seeking_alpha.mdb_sa_history import mdb_sa_history


def run_screener_update(perpage=30):
    """Refresh Seeking Alpha screener result CSVs (symbol lists per portfolio)."""
    screeners = apis.get_sa_screener_details_list()
    nscreeners = apis.filter_to_top_screeners(screeners)
    resultsdict = apis.adict_screener_details(nscreeners, perpage=perpage)
    apis.change_value_to_list(resultsdict)
    apis.replacedot(resultsdict)
    path = __import__("os").path.join(md.data_dir, md.sa)
    apis.file_api_symbols(resultsdict, path)
    print("Screener CSVs updated under", path)


def main():
    parser = argparse.ArgumentParser(description="Weekly update: SA data -> MongoDB -> CSVs")
    parser.add_argument("--no-screener", action="store_true", help="Skip screener symbol list update")
    parser.add_argument("--no-profile", action="store_true", help="Skip symbol profile update")
    parser.add_argument("--no-info", action="store_true", help="Skip symbol info (key data) update")
    parser.add_argument("--no-sa-history", action="store_true", help="Skip SA portfolio history to MongoDB")
    parser.add_argument("--no-export", action="store_true", help="Skip export to company_data CSV files")
    parser.add_argument("--screener-only", action="store_true", help="Only run screener update then exit")
    parser.add_argument(
        "--profile-refresh",
        action="store_true",
        help="Use weekly profile refresh: API -> symbol_profile_cache -> symbol_profile (reports API call count for RapidAPI subscription)",
    )
    args = parser.parse_args()

    if not md.seeking_alpha_key:
        print("SEEKING_ALPHA_KEY not set. Set it in the environment.", file=sys.stderr)
        sys.exit(1)
    if not md.data_dir:
        print("SM_DATA_DIR not set. Set it in the environment.", file=sys.stderr)
        sys.exit(1)

    start = datetime.now()
    print("Weekly update started at", start.isoformat())

    try:
        if not args.no_screener:
            print("\n--- Screener update ---")
            run_screener_update()
        if args.screener_only:
            print("Screener-only run done.")
            return

        if not args.no_profile:
            print("\n--- Symbol profile update ---")
            if args.profile_refresh:
                refresh_symbol_profile_cache(delay_seconds=0.5)
                sync_profile_cache_to_symbol_profile()
            else:
                update_symbol_profile()

        if not args.no_info:
            print("\n--- Symbol info update ---")
            update_symbol_info()

        if not args.no_sa_history:
            print("\n--- SA portfolio history ---")
            mdb_sa_history()

        if not args.no_export:
            print("\n--- Export to CSV ---")
            run_export()
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)

    elapsed = (datetime.now() - start).total_seconds()
    print("\nWeekly update finished in {:.1f}s".format(elapsed))


if __name__ == "__main__":
    main()
