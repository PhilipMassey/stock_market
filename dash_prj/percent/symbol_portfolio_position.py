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
import analysis

label_size = '10px'


results_date = html.Div('Current date',id='results-date',
                        style={'width': '100%', 'text-align': 'center','font-size':label_size})


dirs = md.get_portfolio_dirs()
dropdowns = html.Div([
        html.Div([
            html.Label('Portfolio Directories'),
            dcc.Dropdown(id='dropdown-dirs', options=[{'label': i, 'value': i} for i in dirs], value=None)],
            style={'width': '49%', 'float': 'left'}
            ),
    html.Div([
       html.Label('Portfolios'),
        dcc.Dropdown(id='dropdown-ports', options=[], value=None)],
        style = {'width': '49%','float': 'right'}
    ),

], style= {'width': '100%','display': 'inline-block'})

results_table = html.Div(id="results-table")


app = dash.Dash(__name__)
app.layout = html.Div([results_date, dropdowns, results_table])


#callback on directory selection
@app.callback(
    Output('dropdown-ports', 'options'),
    [Input('dropdown-dirs', 'value')])
def update_dropdown_ports(value):
    if(value != None):
        df_port_symbols = md.get_dir_port_symbols(value)
        return [{'label': i, 'value': i} for i in sorted(df_port_symbols["portfolio"].unique())]
    else:
        return []


@app.callback(
    Output('results-date', 'children'),
    Output('results-table', 'children'),
    Input('dropdown-dirs', 'value'),
    Input('dropdown-ports', 'value')
)
def update_table(directory, portfolio):
    if directory == None or len(directory) == 0:
        df = pd.DataFrame({'Status': ['depends']})
    else:
        if portfolio is not None:
            df = analysis.df_sym_port_pos(portfolio)
        else:
            df = analysis.df_directory_sym_port_pos(directory)
    return (md.get_date_for_ndays(0),
             dt.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                 style_cell={
                     'font_family': 'arial',
                     'font_size': '20px',
                     'text_align': 'right',
                     'maxWidth': '100px'
                 },
                 style_cell_conditional=[
                     {
                     'if': {'column_id': 'Portfolio'},
                     'textAlign': 'left',
                      },
                     {
                         'if': {'column_id': 'Sector'},
                         'textAlign': 'left','maxWidth': '200px'
                     },
                     {
                         'if': {'column_id': 'Industry'},
                         'textAlign': 'left','maxWidth': '200px'
                     },
                     {'if': {'column_id': 'Portfolio'},
                      'maxWidth': '250px'},
                 ],
                sort_action='native'))

if __name__ == '__main__':
    app.run_server(debug=True,port=7001)