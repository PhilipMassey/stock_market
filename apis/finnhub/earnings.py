import finnhub
import pandas as pd
finnhub_client = finnhub.Client(api_key="sandbox_c6jdbjqad3ieecon3j7g")
symbol = 'BLDR'


res = finnhub_client.company_earnings_quality_score(symbol, 'quarterly')
#res = finnhub_client.company_earnings_quality_score(symbol, 'yearly')
#df = pd.DataFrame(res)
#df.columns = Index(['data', 'freq', 'symbol'], dtype='object')
df = pd.DataFrame.from_dict(res['data'])
print(df)