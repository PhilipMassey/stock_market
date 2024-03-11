import warnings
warnings.filterwarnings('ignore')

from market_data.exchange.FidelityPositions import FidelityPositions


if __name__ == '__main__':
        fidelity_positions = FidelityPositions()
        fidelity_positions.df_fidelity_positions_load()
        fidelity_positions.df_aggregate_columns()
        fidelity_positions.order_columns()
        fidelity_positions.add_to_mdb()

        fidelity_positions.fidlelity_postions_xlsx_update()
        fidelity_positions.print_differences()
        fidelity_positions.holding_portfolios_update()
