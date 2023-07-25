import market_data as md
import pandas as pd
import apis
import performance as pf

def int_to_en(num):
    d = { 0 : '0', 1 : '1', 2 : '2', 3 : '3',4: '4', 5 : '5',6 : '6', 7 : '7', 8 : '8', 9 : '9',
          10:'10',11:'11',12:'12',13:'13',14:'14',15:'15',16:'16',17:'17',18:'18',19:'19',
          20:'20',21:'21',22:'22',23:'23',24:'24',25:'25',26:'26',27:'27',28:'28',29:'29',
          30:'30',31:'31',32:'32',33:'33',34:'34',35:'35',36:'36',37:'37',38:'38',39:'39',
          40:'40',41:'41',42:'42',43:'43',44:'44',45:'45',46:'46',47:'47',48:'48',49:'49',
          50:'50',51:'51',52:'52',53:'53',54:'54',55:'55',56:'56',57:'57',58:'58',59:'59',
          60:'60',61:'61',62:'62',63:'63',64:'64',65:'65'
          }
    return d[num]



def holding_non_sa(directory,port):
    if port == None or len(port) == 0:
        symbols = md.get_symbols(directory)
    else:
        symbols = md.get_symbols_dir_and_port(directory=directory, port=port)
    sa_symbols = md.get_symbols('Seeking_Alpha')
    non_sa_symbols = sorted(set(symbols).difference(set(sa_symbols)))
    return sorted(set(non_sa_symbols))


def df_non_sa(directory, port):
    non_sa_symbols = holding_non_sa(directory,port)
    dfnsa = pd.DataFrame({'Non SA':non_sa_symbols})
    dfnsa =dfnsa.T
    dfnsa.columns = [int_to_en(column) for column in dfnsa.columns]
    dfnsa.reset_index(inplace=True)
    dfnsa.rename(columns={'index':'Portfolio'},inplace=True)
    return dfnsa

def df_symbols_by_sa_ports(symbols,directory, port):
    sa_ports = md.sa_sectors
    dct = {}
    for sa_port in sa_ports:
        quant = md.get_symbols_for_portfolios([sa_port])
        symbolsx = sorted(set(symbols).intersection(set(quant)))
        #print(port, ': ', symbols)
        dct[sa_port] = symbolsx
    df = pd.DataFrame.from_dict(dct, orient='index')
    df.columns = [int_to_en(column) for column in df.columns]
    df.reset_index(inplace=True)
    df.rename(columns={'index':'Portfolio'},inplace=True)
    if directory == 'Holding':
        df_non_sa_symbols = df_non_sa(directory, port)
        df = pd.concat([df,df_non_sa_symbols])
    return df


def df_symbols_by_sector(symbols):
    fields = ['symbol','sectorname','primaryname']
    df = apis.df_symbol_profile(symbols, fields)
    df.dropna(inplace=True)
    dct = {}
    for sector in df.sectorname.values:
        dct[sector] = sorted(list(df[df.sectorname==sector].symbol.values))
    df =pd.DataFrame.from_dict(dct, orient='index')
    df
    df.columns = [int_to_en(column) for column in df.columns]
    df.reset_index(inplace=True)
    df.rename(columns={'index':'Sector'},inplace=True)
    return df.sort_values(by='Sector')


def df_symbols_by_portfolio(symbols, directory):
    df_ports_symbols = md.get_port_and_symbols(directory)
    df = df_ports_symbols[df_ports_symbols.symbol.isin(symbols)]
    dct = {}
    for port in df.portfolio.values:
        dct[port] = sorted(list(df[df.portfolio==port].symbol.values))

    df =pd.DataFrame.from_dict(dct, orient='index')
    df.columns = [int_to_en(column) for column in df.columns]
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Portfolio'}, inplace=True)
    return df

def reorder_cols(df):
    cols = list(df.columns)
    end = len(cols)-2
    rcols = cols[:end]
    ucols = [cols[-2],cols[-1]]
    ucols.extend(rcols)
    return df[ucols]


def dct_sector_symbols(symbols):
    fields = ['symbol', 'sectorname', 'primaryname']
    df = apis.df_symbol_profile(symbols, fields)
    df.dropna(inplace=True)
    dct = {}
    for sector in df.sectorname.values:
        dct[(sector)] = sorted(list(df[(df.sectorname == sector)].symbol.values))
    return dct


def df_sector_means_for_range(ndays_range,symbols):
    dct = dct_sector_symbols(symbols)
    dfall = pd.DataFrame({})
    for sector in dct.keys():
        dct_symbols = (dct[sector])
        calc_percent = pf.calc_interval_between
        df = pf.df_closing_percent_change(ndays_range, calc_percent, dct_symbols)
        dfs = df.describe()
        df = dfs.loc['mean'].to_frame().T.reset_index() #.rename(columns={'index':sector})
        df.replace('mean',sector,inplace=True)
        dfall = pd.concat([dfall,df])
    dfall = dfall.sort_values(by=['index']).round(decimals=2).rename(columns={'index':'Sector'})
    return dfall


def dct_sector_industry_symbols(symbols):
    fields = ['symbol', 'sectorname', 'primaryname']
    df = apis.df_symbol_profile(symbols, fields)
    df.dropna(inplace=True)
    dct = {}
    for sector in df.sectorname.values:
        for industry in df[df.sectorname == sector].primaryname.values:
            dct[(sector, industry)] = sorted(
                list(df[(df.sectorname == sector) & (df.primaryname == industry)].symbol.values))
    return dct


def df_sector_industry_means_for_range(ndays_range,symbols):
    dct = dct_sector_industry_symbols(symbols)
    dfall = pd.DataFrame({})
    for sector_industry in dct.keys():
        dct_symbols = dct[(sector_industry)]
        calc_percent = pf.calc_interval_between
        df = pf.df_closing_percent_change(ndays_range, calc_percent, dct_symbols)
        dfs = df.describe()
        df = dfs.loc['mean'].to_frame().T.reset_index() #.rename(columns={'index':sector})
        df.replace('mean',sector_industry,inplace=True)
        dfall = pd.concat([dfall,df])
    dfall = dfall.sort_values(by=['index']).round(decimals=2).rename(columns={'index':'Sector'})
    return dfall


def df_symbols_by_sector_industry(symbols):
    fields = ['symbol','sectorname','primaryname']
    df = apis.df_symbol_profile(symbols, fields)
    df.dropna(inplace=True)
    dct = {}
    for sector in df.sectorname.values:
        for industry in df[df.sectorname==sector].primaryname.values:
            dct[(sector,industry)] = sorted(list(df[(df.sectorname==sector) & (df.primaryname==industry)].symbol.values))

    df =pd.DataFrame.from_dict(dct, orient='index')
    df.columns = [int_to_en(column) for column in df.columns]
    df['Sector'] = [l[0] for l in df.index.values]
    df['Industry'] = [l[1] for l in df.index.values]
    df.reset_index(inplace=True)
    df.drop(columns=['index'],inplace=True)
    #df.sort_values(by='Sector',inplace=True)
    df.sort_values(by=['Sector', 'Industry'],inplace=True)
    df = reorder_cols(df)
    return df

