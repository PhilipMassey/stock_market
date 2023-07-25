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

label_size = '18px'

results_date = html.Div('Current date',id='results-date',
                        style={'width': '100%', 'text-align': 'center','font-size':label_size})

label_perc_or_mean = html.Label('Perc or Mean',style={'font-size':label_size})
radio_perc_or_mean = html.Div([
    dcc.RadioItems(
        id='radio-perc-or-mean',
        options=[
            {'label': 'Portfolio Mean', 'value': pf.mean_option},
            {'label': 'Symbol percent change', 'value': pf.perc_option}
            ],
       labelStyle={'display': 'block'},
       value=pf.perc_option, ),
])


label_ndays_range = html.Label('Select Period', style={'font-size':label_size})
radio_ndays_range = html.Div([
    dcc.RadioItems(
        id='radio-ndays-range',
        options=[
            {'label': '5, 10, 21, 64, 128, 252 days', 'value': pf.calc_percent_year},
            {'label': '2 Months', 'value': pf.calc_percent_2monthly},
            {'label': '1 Month', 'value': pf.calc_percent_monthly},
            {'label': '2 Weeks', 'value': pf.calc_percent_2weekly},
            {'label': '1 Week', 'value': pf.calc_percent_weekly},
            {'label': 'Daily', 'value': pf.calc_percent_daily}
        ],
        labelStyle={'display': 'block'},
        value=pf.calc_percent_weekly, ),
])


label_calc_percent = html.Label('Calc percent', style={'font-size':label_size})
radio_calc_percent = html.Div([
    dcc.RadioItems(
        id='radio-calc-percent',
        options=[
            {'label': 'Calc overall', 'value': pf.calc_interval_overall},
            {'label': 'Calc between', 'value': pf.calc_interval_between}
        ],
        labelStyle={'display': 'block'},
        value=pf.calc_interval_between, ),
])


perc_or_mean_block = html.Div([label_perc_or_mean, radio_perc_or_mean],
                         style={'width': '33%', 'display': 'inline-block'})
ndays_range_block = html.Div([label_ndays_range, radio_ndays_range],
                             style={'width': '33%', 'display': 'inline-block'})
calc_interval_block = html.Div([label_calc_percent, radio_calc_percent],
                               style={'width': '33%', 'display': 'inline-block', 'float': 'right'})

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
app.layout = html.Div([results_date, perc_or_mean_block, ndays_range_block,
                   calc_interval_block, dropdowns,
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
    Input('radio-calc-percent', 'value'),
    Input('radio-ndays-range', 'value'),
    Input('radio-perc-or-mean', 'value'),
    Input('dropdown-dirs', 'value'),
    Input('dropdown-ports', 'value')
)
def update_table(calc_percent, opt_ndays_range, perc_or_mean, directory, port):
    results_date_value = 'No results'
    if directory is None:
        ndays_range = md.get_ndays_periods(months=list(range(12, 0, -2)))
        df = pd.DataFrame({'directory':[directory], 'symbol':[port]})
    else:
        ndays_range = pf.get_ndays_range(opt_ndays_range)
        if perc_or_mean == pf.perc_option:
            symbols = md.get_symbols_dir_or_port(directory=directory, port=port)
            if directory == 'holding' or port is not None:
                df = pf.df_closing_percent_change(ndays_range, calc_percent, symbols)
                #df = pf.df_closing_percent_change_current(ndays_range, calc_percent, symbols)
            else:
                df = pf.df_closing_percent_change(ndays_range, calc_percent, symbols)
        elif perc_or_mean == pf.mean_option:
            df = pf.df_dir_ports_means_for_range(ndays_range, calc_percent, directory)
    return (md.get_date_for_ndays(ndays_range[-1]),
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


