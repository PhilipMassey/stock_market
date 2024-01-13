import market_data as md

class FidelityPositionsRunner:
    def __init__(self):
        pass

    def execute(self):
        df = self.get_fidelity_positions()
        sum_df = self.aggregate_columns(df)
        sum_df = self.calculate_current_return(sum_df)
        self.filter_to_portfolio_and_file(sum_df, 'Alpha Picks', md.sa)
        self.filter_to_portfolio_and_file(sum_df, 'Dividends', md.proforma)
        self.filter_to_portfolio_and_file(sum_df, 'ETFs', md.proforma)
        self.filter_to_portfolio_and_file(sum_df, 'Stocks', md.proforma)

    def get_fidelity_positions(self):
        return md.df_fidelity_positions()

    def aggregate_columns(self, df):
        return md.df_aggregate_columns(df)

    def calculate_current_return(self, sum_df):
        return md.df_calculate_current_return(sum_df)

    def filter_to_portfolio_and_file(self, sum_df, portfolio, directory):
        return md.filter_to_portfolio_and_file(sum_df, directory, portfolio)