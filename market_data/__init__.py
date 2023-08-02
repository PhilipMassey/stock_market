from os.path import join
import os
seeking_alpha_key = os.environ.get('SEEKING_ALPHA_KEY')
data_dir = os.environ.get('SM_DATA_DIR')


#FOLDERS
all = 'ALL'
ark = 'ARK'
etf = 'ETF'
holding = 'holding'
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
db_seeking_alpha_history = 'seeking_alpha_history'
db_holding_history = 'holding history'

from .csv_data_defs import *
from .portfolio_defs import *
from .stock_mdb import *
from .exchange_api import *


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
            'Top Consumer Staples Stocks',
            'Top Energy Stocks',
            'Top Financial Stocks',
            'Top Healthcare Stocks',
            'Top Industrial Stocks',
            'Top Materials Stocks',
            'Top REITs',
            'Top Real Estate Stocks',
            'Top Technology Stocks',
            'Top Utility Stocks',
            'Top Yield Monsters'
            ]

sa_others = ['Top ETFs by Quant',
             'Top Rated Stocks',
             'Top Stocks by Quant',
             'Top Value Stocks']

symbols_not_in_yahoo = []