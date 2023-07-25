import requests
import json
import http.client
import market_data as md
import pandas as pd
import apis as ra_apis
conn = http.client.HTTPSConnection("seeking-alpha.p.rapidapi.com")

headers = {
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
    'x-rapidapi-key': md.seeking_alpha_key
    }

profile_fields = ['profile.sectorname','profile.sectorgics','profile.primaryname','profile.primarygics','profile.numberOfEmployees','profile.yearfounded','profile.streetaddress','profile.streetaddress2','profile.streetaddress3','profile.streetaddress4','profile.city','profile.state','profile.zipcode','profile.country','profile.officephonevalue','profile.webpage','profile.companyName','profile.marketCap','profile.totalEnterprise','profile.totAnalystsRecommendations','profile.fy1UpRevisions','profile.fy1DownRevisions','profile.divYield','profile.eps','profile.lastDaily.rtTime','profile.lastDaily.rtSource','profile.lastDaily.last','profile.lastDaily.open','profile.lastDaily.close','profile.lastDaily.low','profile.lastDaily.high','profile.lastDaily.volume','profile.lastDaily.volumeAt','profile.lastDaily.at','profile.estimateEps','profile.debtEq','profile.totDebtCap','profile.ltDebtEquity','profile.ltDebtCap','profile.totLiabTotAssets','profile.impliedMarketCap','profile.shortIntPctFloat','profile.divTimeFrame','profile.divRate','profile.peRatioFwd','profile.lastClosePriceEarningsRatio','profile.estimateFfo','profile.ffoPerShareDiluted','profile.dilutedEpsExclExtraItems','profile.high52','profile.low52']

def dct_api_symbol_profile(symbols):
    dct_symbol_profile = {}
    for idx in range(0,len(symbols),4):
        symbols4= "%2C".join(symbols[idx:idx+4])

        conn.request("GET", "/symbols/get-profile?symbols=" + symbols4, headers=headers)

        res = conn.getresponse()
        data = res.read()
        txt = data.decode("utf-8")
        if 'data' not in txt:
            print('No data ',symbols)
            continue
        ldcts = json.loads(txt)['data']
        for idx in range(len(ldcts)):
            dct_symbol_profile[ldcts[idx]['id']] = ldcts[idx]['attributes']

    return dct_symbol_profile


def mdb_add_symbols_profiles_for_directory(ndays,directory, db_coll_name):
    ports = md.get_ports_for_directory(directory)
    mdb_symbols = md.mdb_profile_get_symbols()
    for port in ports:
        print('\t',port, end=': ')
        symbols = md.get_symbols(ports=[port])
        not_added_symbols = set(symbols).difference(set(mdb_symbols))
        print(len(not_added_symbols))
        if len(not_added_symbols) > 0:
            print('\t\t no profile: ', not_added_symbols)
            dct_api = dct_api_symbol_profile(list(not_added_symbols))
            if len(dct_api) != 0:
                df = pd.DataFrame.from_dict(dct_api)
                df = df.T.reset_index().rename(columns={'index':'symbol'})
                md.df_add_date_column(ndays,df)
                inserted = md.mdb_add_df(df,db_coll_name)
                #print(inserted)
                mdb_symbols.extend(not_added_symbols)

def update_symbol_profile():
    print('running update_symbol_info')
    dirs = md.get_directorys()
    ndays = 0
    db_coll_name = md.db_symbol_profile
    for directory in dirs:
        print('Directory: ',directory)
        mdb_add_symbols_profiles_for_directory(ndays, directory, db_coll_name)


if __name__ == '__main__':
    update_symbol_profile()