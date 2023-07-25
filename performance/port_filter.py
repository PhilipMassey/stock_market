import market_data as md

def filteredbySymbols(df, incl,colorrow='row'):
    symbols = md.get_symbols(incl)
    if colorrow == 'row':
        return df[df.symbol.isin(symbols)]
    elif colorrow == 'col':
        return df.filter(items=symbols)


def filteredbyPortfolios(df,incl):
    portfolios = md.get_portfolios(incl)
    return df[df.portfolio.isin(portfolios)]

