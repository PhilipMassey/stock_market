import market_data as md

df = md.df_fidelity_positions()
sum_df = md.df_aggregate_columns(df)
sum_df = md.df_calculate_current_return(sum_df)

portfolio = 'Alpha Picks'
directory = md.sa
md.filter_to_portfolio_and_file(sum_df, directory, portfolio)
portfolio = 'Dividends'
directory = md.proforma
md.filter_to_portfolio_and_file(sum_df, directory, portfolio)
portfolio = 'ETFs'
directory = md.proforma
md.filter_to_portfolio_and_file(sum_df, directory, portfolio)
portfolio = 'Stocks'
directory = md.proforma
md.filter_to_portfolio_and_file(sum_df, directory, portfolio)
