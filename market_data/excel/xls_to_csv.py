import sys; sys.path.extend(['/Users/philipmassey/PycharmProjects/stock_market'])
sys.path.extend(['/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages'])

import market_data as md
import os
from os.path import isfile, join
from os import listdir
import pylightxl as xl
import re

rpath = '/Users/philipmassey/Downloads/Investing/Firefox/'
budir = join(rpath,'bu')
wpath = join(md.data_dir, 'Seeking_Alpha')

def conform_to_spec(tkrs):
    tkrs = tkrs[:12]
    return [l.replace('.','-') for l in tkrs]

def xlsx_to_csv(rpath,xlsx_filen,wpath):
    xlsx_filep = join(rpath,xlsx_filen)
    print(xlsx_filep)
    db = xl.readxl(fn = xlsx_filep)
    itr = iter(db.ws(ws=db.ws_names[0]).cols)
    next(itr)
    tkrs = next(itr)
    tkrs = conform_to_spec(tkrs)
    #print(tkrs)
    m = re.search(r"\d", xlsx_filen)
    cvs_filen = xlsx_filen[0:m.start()].strip() + '.csv'
    write_to_csv(tkrs,wpath,cvs_filen)

def write_to_csv(tkrs,wpath,cvs_filen):
    cvs_filep = join(wpath,cvs_filen)
    print(cvs_filen)
    f = open(cvs_filep, 'w')
    for tkr in tkrs:
        f.write(tkr + '\n')
    f.close()

def move_to_backup(rpath,fname,budir):
    os.rename(join(rpath,fname),join(budir,fname))

xlsx_filesn = [f for f in listdir(rpath) if isfile(join(rpath, f))]
for xlsx_filen in xlsx_filesn:
    if xlsx_filen.endswith(".xlsx"):
        xlsx_to_csv(rpath,xlsx_filen,wpath)
        move_to_backup(rpath,xlsx_filen,budir)
