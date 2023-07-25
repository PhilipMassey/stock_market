import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = [20, 3]
import yfinance as yf

def barPlotPctChangedf(symbol, interval, period):
    df= yf.download(symbol,interval=interval,rounding=True, period=period,auto_adjust=True)
    pct_change = df.Close.pct_change(periods=1)
    close_ma30 = pd.concat([df.Close, pct_change], axis=1).dropna()
    close_ma30.columns = ['Close', 'pct_change']
    close_ma30['pct_change'].plot(kind='bar')
    plt.show()

#interval : 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
#ndays_range :   1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max   or start and end
symbol = 'CDEV'
barPlotPctChangedf(symbol,'90m','1mo')
barPlotPctChangedf(symbol,'1d','3mo')
barPlotPctChangedf(symbol,'1wk','6mo')