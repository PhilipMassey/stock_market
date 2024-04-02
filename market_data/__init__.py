import os
seeking_alpha_key = os.environ.get('SEEKING_ALPHA_KEY')
data_dir = os.environ.get('SM_DATA_DIR')
download_dir = os.environ.get('DOWNLOAD_DIR')

#FOLDERS
all = 'ALL'
ark = 'ARK'
etf = 'ETF'
holding = 'Holding'
proforma = 'Proforma'
fidelity_positions = 'Fidelity/Fidelity Positions'
logs = 'logs'
sa = 'Seeking_Alpha'
sa_history = 'sa_history'
test = 'test'
watching = 'Watching'
db_client = 'stock_market'
db_close = 'market_data_close'
db_volume = 'market_data_volume'
db_test_close = 'test_close'
db_test_vol = 'test_volume'
db_symbol_profile = 'symbol_profile'
db_symbol_info = 'symbol_info'
db_fidel_pos = 'FidelityPositions'
portfolio_proforma = 'Portfolio Proforma'
dct_sheet_url = {
    'Portfolio Proforma': 'https://docs.google.com/spreadsheets/d/15FDENGNSt6n-iKfWwX9nqqrXVFwN5Cp0GWQXxlaw_x4/edit#gid=0',
    'Portfolio Adjustments': 'https://docs.google.com/spreadsheets/d/1bTsH3cjQDGR-Mlnq-bypRqhGIHJApKKJgsgXWSemur4/edit#gid=0'}
dct_proforma_id = {'Alpha Picks': 1375800256, 'Dividends': 0, 'ETFs': 1884178483, 'International': 874195600,
                        'Stocks': 462380812, 'Treasuries': 335039254}
dct_adjustment_id = {'Alpha Picks': 0, 'Dividends': 1022929694, 'ETFs': 84489004, 'International': 1766130281,
                          'Stocks': 569122364, 'Treasuries': 1853636016, 'Fidelity Positions': 1064903312}

from market_data.exchange.csv_data_defs import *
from market_data.exchange.portfolio_defs import *
from market_data.exchange.FidelityPositions import *
from .stock_mdb import *
from .exchange_api import *
from .exchange import *
from .xlsx_data import *

test_symbols = 'test_symbols'
top_growth_stocks = 'Top Growth Stocks'
top_reits = 'Top REITs'
top_rated_dividend_stocks = 'Top Rated Dividend Stocks'
top_rated_stocks = 'Top Rated Stocks'
top_small_cap_stocks = 'Top Small Cap Stocks'
top_stocks_by_quant = 'Top Stocks by Quant'
top_stocks_in_renewable_electricity = 'Top Stocks in Renewable Electricity'
top_value_stocks = 'Top Value Stocks'
utilities = 'Utilities'
utilities_renewable_energy = 'Utilities-Renewable Energy'
water_etf = 'Water ETF'

sa_sectors = ['Top Communication Stocks',
            'Top Consumer Discretionary Stocks',
            'Top Energy Stocks',
            'Top Financial Stocks',
            'Top Healthcare Stocks',
            'Top Industrial Stocks',
            'Top Materials Stocks',
            'Top Technology Stocks'
            ]

sa_top_screeners = ['Stocks by Quant',
             'Top Rated Stocks']



symbols_not_in_yahoo = []