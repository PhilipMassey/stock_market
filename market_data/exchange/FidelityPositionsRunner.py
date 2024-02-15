import warnings
warnings.filterwarnings('ignore')

from market_data.exchange.FidelityPositions import FidelityPositions


if __name__ == '__main__':
    try :
        filelity_positions = FidelityPositions()
        filelity_positions.execute()
        filelity_positions.print_differences()
    except Exception as e:
        print(e)