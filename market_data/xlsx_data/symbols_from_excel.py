import market_data as md
import pandas as pd
import glob
from os.path import join


def xlsx_filens(directory):
    files = glob.glob(directory + '/*.xlsx')
    return files


def write_sa_csv(filep, symobls):
    sa_filen = filep[30:-15]
    fpath = join(md.data_dir, md.sa, sa_filen + '.csv')
    with open(fpath, 'w') as f:
        f.write('Symbol\n' + '\n'.join(symbols))
        f.close()


directory = md.download_dir
fileps = xlsx_filens(directory)

for filep in fileps:
    print(filep)
    df = pd.read_excel(filep)
    symbols = df.Symbol.values
    write_sa_csv(filep, symbols)

