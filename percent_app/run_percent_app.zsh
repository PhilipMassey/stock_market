
export PYTHONPATH=/Users/philipmassey/stock_market
export SM_DATA_DIR=/Users/philipmassey/stock_market/market_data
cd /Users/philipmassey/stock_market/percent_app
nohup ../.venv/bin/python ./app.py  > /Users/philipmassey/percent_app.log 2>&1 &