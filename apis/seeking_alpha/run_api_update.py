import requests
import pandas as pd
import json
import os
from os.path import join
import market_data as md
import apis

exclude_screeners = ["Earnings Season's Strong Sells",
"Top Energy by SA Authors ",
"Most Shorted Stocks",
"Strong Buy Stocks With Short Squeeze Potential",
"Top Real Estate Stocks"]
#"Earnings Season's Top Stocks",

screeners = apis.get_sa_screener_details_list()
nscreeners = apis.filter_to_top_screeners(screeners)
resultsdict = apis.adict_screener_details(nscreeners, perpage=30)
apis.change_value_to_list(resultsdict)
apis.replacedot((resultsdict))
print('\nNo of portfolios: ',len(resultsdict.keys()))
for key in resultsdict.keys():
    print(key, len(resultsdict[key]))
resultsdict
subdir = md.sa
path = os.path.join(md.data_dir, subdir)
apis.file_api_symbols(resultsdict, path)




