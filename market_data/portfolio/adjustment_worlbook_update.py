import market_data as md
import pandas as pd
from os.path import join


def df_resolve_alpha_picks_proforma():
    df = md.df_from_google_spreadsheet(md.portfolio_proforma, md.dct_proforma_id['Alpha Picks'])
    df = df.drop(columns=df.columns[df.columns.str.contains('Unnamed')])
    df = df.dropna()
    df = df.groupby('Symbol').agg(
        {'Holding %': 'sum', 'Sector': 'first', 'Rating': 'first', 'Company': 'first', 'Picked': 'first',
         'Return': 'sum'}).reset_index()
    result = md.worksheet_update_with_df(md.portfolio_proforma,md.dct_proforma_id['Alpha Picks'],df)
    return df

def file_proforma_folders():
    portfolios = md.portfolios
    path = join(md.data_dir, 'Proforma')
    for portfolio in portfolios:
        df = md.df_from_google_spreadsheet(md.portfolio_proforma, md.dct_proforma_id[portfolio])
        symbols = df.Symbol.values
        symbols = sorted(list(symbols))
        fpath = join(path, portfolio + ".csv")
        with open(fpath, 'w') as f:
            f.write('Symbol\n' + '\n'.join(symbols))
            f.close()
    print('Completed Filing Proforma folders ', path)


def update_adjustments_workbook_from_fidelity_and_proformas_workbooks(portfolios):
    positions_df = md.df_from_google_spreadsheet(md.portfolio_proforma, md.dct_proforma_id['Fidelity Positions'])
    workbook_name = md.portfolio_adjustments
    for portfolio_name in portfolios:
        proforma_df = md.df_from_google_spreadsheet(md.portfolio_proforma, md.dct_proforma_id[portfolio_name])
        filtered_df = positions_df[positions_df['Symbol'].isin(proforma_df.Symbol)]
        merged_df = pd.merge(filtered_df[['Symbol', 'Current Value', 'Cost Basis Total']], proforma_df, on='Symbol',
                             how='inner')
        df = merged_df
        df['Buy/Sell %'] = 0
        df['Buy/Sell $'] = 0
        df['Current Value %'] = 0
        df['Current Value %'] = 0
        df['Current Return %'] = 0
        df = df[['Symbol', 'Buy/Sell $', 'Current Value', 'Current Return %', 'Rating', 'Current Value %',
                 'Holding %', 'Buy/Sell %', 'Cost Basis Total']]
        worksheet_id = md.dct_adjustment_id[portfolio_name]
        result = md.worksheet_update_with_df(workbook_name, worksheet_id, df)

if __name__ == '__main__':
    portfolios = md.portfolios
    #portfolios = ['Shorts']
    print('Updating Adjustments worksheets from Fidelity Positions worksheet for Portfolios: ', portfolios)
    update_adjustments_workbook_from_fidelity_and_proformas_workbooks(portfolios)

