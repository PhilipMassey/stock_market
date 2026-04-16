import yfinance as yf
import requests

# Create a session with a significantly larger thread/connection pool
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=200, pool_maxsize=200)
session.mount('https://', adapter)

def get_yahoo_ndays_ago_jupyter(ndays, symbols):
    from_date, to_date = md.get_fromdate_and_todate(ndays - 1)
    
    # Pass the custom session directly to yfinance
    df = yf.download(
         tickers=symbols, interval="1d", start=from_date, end=to_date, 
         group_by='column', auto_adjust=True, prepost=True, 
         threads=True, session=session
    )
    if df.size == 0:
        print('no results from yahoo')
        sys.exit(1)
    return df[['Close']]

