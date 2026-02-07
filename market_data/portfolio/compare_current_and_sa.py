import market_data as md
import pandas as pd
from os import listdir
from os.path import isfile, join, isdir

def symbols_in_file(port):
    holding_symbols = md.get_symbols_dir_and_port(md.holding , port)
    sa_symbols = md.get_symbols_dir_and_port(md.sa, 'Current ' + port)
    return set(holding_symbols).difference(set(sa_symbols)),set(sa_symbols).difference(set(holding_symbols))

if __name__ == '__main__':
    for port in md.portfolios:
        holding, sa = symbols_in_file(port)
        print('Current: ',port ,'\t\tadd: ',holding ,' remove: ',sa)
