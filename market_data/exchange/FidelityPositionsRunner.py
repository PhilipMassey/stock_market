import warnings
warnings.filterwarnings('ignore')

from market_data.exchange.FidelityPositions import FidelityPositions


if __name__ == '__main__':
    try :
        filelity_positions = FidelityPositions()
        filelity_positions.fidlelity_postions_xlsx_update()
        filelity_positions.print_differences()
        filelity_positions.holding_portfolios_update()
    except Exception as e:
        print(e)