import yfinance as yf
from datetime import datetime, timedelta

symbols = ['AAPL', 'MSFT', 'GOOG']
# yfinance occasionally hangs when downloading multiple tickers in standalone scripts,
# let's see if we reproduce it.
from_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
to_date = datetime.now().strftime('%Y-%m-%d')

df = yf.download(tickers=symbols, interval="1d", start=from_date, end=to_date, group_by='column',
                 auto_adjust=True, prepost=True, threads=True)
print(df.head())
