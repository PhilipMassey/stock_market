import warnings
warnings.filterwarnings('ignore')

from market_data.exchange.FidelityPositions import FidelityPositions
import market_data as md

if __name__ == '__main__':
        fidelity_positions = FidelityPositions()
        fidelity_positions.df_fidelity_positions_load()
        fidelity_positions.add_to_mdb()
        fidelity_positions.df_aggregate_columns()
        fidelity_positions.order_and_add_columns()
        #fidelity_positions.fidlelity_postions_xlsx_update()
        fidelity_positions.fidelity_positions_worksheet_update()
        fidelity_positions.print_differences()

