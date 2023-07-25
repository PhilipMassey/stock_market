import dash

from dash import callback
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash import dash_table as dt
from dash.dash_table.Format import Format, Group, Scheme, Trim
from flask import request
import market_data as md
import pandas as pd
import apis

Holding = md.get_port_and_symbols('holding')
holding_portfolios = Holding['portfolio'].unique()
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Input(id="input-symbol", type="text", placeholder="", debounce=True),
        html.Div(id='output-symbol'),
        html.Div(id='listing-table'),
        html.Div(id='details-table'),
    ]
    )



@app.callback(
    Output('output-symbol','children'),
    Output('listing-table', 'children'),
    Output('details-table', 'children'),
    Input('input-symbol', 'value')
)
def update_table(symbol):
    #print(symbol)
    #print(request.args)
    if symbol == None or len(symbol) == 0:
        dfp = pd.DataFrame({'Status': ['depends']})
        dfd = pd.DataFrame({'Status': ['depends'],
                            'Stutas':['less']})
    else:
        symbol = symbol.upper()
        print(symbol)
        portfolios_symbols = md.get_port_and_symbols(directory=md.all)
        portfolios_with_symbols = portfolios_symbols[portfolios_symbols['symbol'] == symbol]['portfolio']
        dct = {'Listed': [port for port in portfolios_with_symbols if port not in holding_portfolios],
               'holding': [port for port in portfolios_with_symbols if port in holding_portfolios]}
        dfp = pd.DataFrame.from_dict(dct, orient='index')
        dfp= dfp.T
        dfd = apis.df_mdb_symbol_profile(symbol)
        #dfd = dfd.T
    return (symbol,dt.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in dfp.columns],
            data=dfp.to_dict('records'),
            style_cell={
                'font_family': 'arial',
                'font_size': '20px',
                'text_align': 'center'
            },
            sort_action='native'),
            dt.DataTable(
                id='table2',
                columns=[
                    dict(id=dfd.columns[0], name=dfd.columns[0], type='any', format=Format()),
                    #dict(id=dfd.columns[1], name=dfd.columns[1], type='numeric', format=Format(precision=4).group(True))
                    dict(id=dfd.columns[1], name=dfd.columns[1], type='numeric', format=Format(scheme=Scheme.decimal_si_prefix,precision=3))
                ],
            data=dfd.to_dict('records'),
                style_cell={
                    'font_family': 'arial',
                    'font_size': '16px',
                    'text_align': 'left',
                },
                sort_action='native'),
            )

if __name__ == '__main__':
    app.run_server(debug=True,port=7001)