#!/bin/bash

export PYTHONPATH=/Users/philipmassey/stock_market
export SM_DATA_DIR=/Users/philipmassey/stock_market/market_data
cd /Users/philipmassey/stock_market/


./.venv/bin/python ./market_data/scripts/run_mdb_missing.py
#nohup ../.venv/bin/python ./run_mdb_missing.py
#> ~/run_mdb_missing.log 2>&1 &
echo "Finished running load_missing.py."
