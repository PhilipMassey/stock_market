import dash
#dash.register_page(__name__, path="/")
from dash import callback
from dash import html
from dash import dcc
from dash import dash_table as dt
from dash.dependencies import Output, Input
import market_data as md
import performance as pf
import pandas as pd
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_extensions import EventListener
import webbrowser
import apis
import analysis

label_size = '18px'

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
listen_table = html.Div(
    [
        EventListener(
            id="el",
            events=[{"event": "dblclick", "props": ["srcElement.className", "srcElement.innerText"]}],
            logging=True,
            children=results_table,
        )
    ]
)


dct_profile = apis.dct_mdb_symbol_names()
def get_tooltip(symbol):
    if symbol in dct_profile:
        return dct_profile[symbol]
    else:
        return 'No worries,mate!'


app = dash.Dash(__name__)
app.layout = html.Div([results_date,
                   dropdowns,
                   listen_table,
                   html.Div(id="event")
                   ])


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


#update table based on
@app.callback(
    Output('results-date','children'),
    Output('results-table', 'children'),
    Input('dropdown-dirs', 'value'),
    Input('dropdown-ports', 'value')
)
def update_table(directory, port):
    results_date_value = 'No results'
    if directory is None:
        df = pd.DataFrame({'directory':[directory], 'symbol':[port]})
    elif port is not None:
        df = analysis.df_port_sa_rating(port)
    else:
        df = analysis.df_directory_sa_rating(directory)
    return (md.get_date_for_ndays(0),
        dt.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        tooltip_data=[
            {
                    'symbol': {'value': get_tooltip(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in df[['symbol']].to_dict('records')
            ],
        data=df.to_dict('records'),
        export_format="csv",
        style_cell={
            'font_family': 'arial',
            'font_size': '20px',
            'text_align': 'right'
        },
        style_cell_conditional=[
        {
            'if': {'column_id': 'symbol'},
            'textAlign': 'left'
        },
            {'if': {'column_id': 'symbol'},
             'maxWidth': '250px'},
        ],
        sort_action='native'))



@app.callback(Output("event", "children"), Input("el", "event"), Input("el", "n_events"))
def click_event(event, n_events):
    # Check if the click is on the active cell.
    if not event or "cell--selected" not in event["srcElement.className"]:
        raise PreventUpdate

    if event["srcElement.className"] == 'dash-cell column-0 cell--selected focused':
        symbol = event['srcElement.innerText']
        webbrowser.open('https://seekingalpha.com/symbol/' + symbol)
        webbrowser.open('https://seekingalpha.com/symbol/' + symbol + '/earnings/estimates')


if __name__ == "__main__":
     app.run_server(debug=True, port = 8056)


