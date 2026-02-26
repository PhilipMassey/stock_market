import dash
from dash import callback
from dash import html
from dash import dcc
from dash import dash_table as dt
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_extensions import EventListener
import webbrowser
import re

import market_data as md
import performance as pf
import pandas as pd
import apis

dash.register_page(__name__, path="/percent_performance")

label_size = '18px'

results_date = html.Div('Current date', id='results-date-1',
                        style={'width': '100%', 'text-align': 'center', 'font-size': label_size})

label_perc_or_mean = html.Label('Perc or Mean', style={'font-size': label_size})
radio_perc_or_mean = html.Div([
    dcc.RadioItems(
        id='radio-perc-or-mean',
        options=[
            {'label': 'Portfolio Mean', 'value': pf.mean_option},
            {'label': 'Symbol percent change', 'value': pf.perc_option}
        ],
        labelStyle={'display': 'block'},
        value=pf.perc_option,
    ),
])

label_ndays_range = html.Label('Select Period', style={'font-size': label_size})
radio_ndays_range = html.Div([
    dcc.RadioItems(
        id='radio-ndays-range',
        options=[
            {'label': '2 Months', 'value': pf.calc_percent_2monthly},
            {'label': '1 Month', 'value': pf.calc_percent_monthly},
            {'label': '2 Weeks', 'value': pf.calc_percent_2weekly},
            {'label': '1 Week', 'value': pf.calc_percent_weekly},
            {'label': 'Daily', 'value': pf.calc_percent_daily}
        ],
        labelStyle={'display': 'block'},
        value=pf.calc_percent_daily),
])

perc_or_mean_block = html.Div([label_perc_or_mean, radio_perc_or_mean],
                              style={'width': '33%', 'display': 'inline-block'})
ndays_range_block = html.Div([label_ndays_range, radio_ndays_range],
                             style={'width': '33%', 'display': 'inline-block'})

dirs = md.get_portfolio_dirs()
dropdowns_ports = html.Div([
    html.Div([
        html.Label('Portfolio Directories'),
        dcc.Dropdown(id='dropdown-dirs-a', options=[{'label': i, 'value': i} for i in dirs], value=None)],
        style={'width': '49%', 'float': 'left'}
    ),
    html.Div([
        html.Label('Portfolios'),
        dcc.Dropdown(id='dropdown-ports-si', options=[], value=None)],
        style={'width': '49%', 'float': 'right'}
    ),
], style={'width': '100%', 'display': 'inline-block'})


# Cleaned up data layer call utilizing the established API module
try:
    df_sector_ind = apis.get_sectors_industry()
except Exception:
    df_sector_ind = pd.DataFrame()


dropdowns_sectors = html.Div([
    html.Div([
        html.Label('Sector'),
        dcc.Dropdown(id='dropdown-sector', options=[], value=None)],
        style={'width': '49%', 'float': 'left'}
    ),
    html.Div([
        html.Label('Industry'),
        dcc.Dropdown(id='dropdown-industry', options=[], value=None)],
        style={'width': '49%', 'float': 'right'}
    ),
], style={'width': '100%', 'display': 'inline-block'})

results_table = html.Div(id="results-table-1")
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
    line = 'Profile not found'
    if symbol in dct_profile:
        line = dct_profile[symbol]
        if line is None:
            line = 'Profile not found'
    return line

layout = html.Div([results_date, perc_or_mean_block, ndays_range_block,
                   dropdowns_ports, dropdowns_sectors,
                   listen_table,
                   html.Div(id="event-1")
                   ])


# =========================================================
# Callbacks
# =========================================================

# Callback on directory selection
@callback(
    Output('dropdown-ports-si', 'options'),
    [Input('dropdown-dirs-a', 'value')])
def update_dropdown_ports(directory):
    if directory is not None:
        df_port_symbols = md.get_dir_port_symbols(directory)
        return [{'label': i, 'value': i} for i in sorted(df_port_symbols["portfolio"].unique())]
    else:
        return []

# Dynamic Callback for Sector Selection (Filters based on selected portfolio!)
@callback(
    Output('dropdown-sector', 'options'),
    [Input('dropdown-dirs-a', 'value'),
     Input('dropdown-ports-si', 'value')]
)
def update_dropdown_sectors(directory, port):
    if not df_sector_ind.empty and 'sector' in df_sector_ind.columns:
        if directory is not None:
             symbols = md.get_symbols_dir_or_port(directory=directory, port=port)
             df_filtered = df_sector_ind[df_sector_ind['symbol'].isin(symbols)]
             sectors = sorted(list(df_filtered['sector'].dropna().unique()))
        else:
             sectors = sorted(list(df_sector_ind['sector'].dropna().unique()))
        return [{'label': i, 'value': i} for i in sectors]
    return []

# Callback on sector selection
@callback(
    Output('dropdown-industry', 'options'),
    [Input('dropdown-sector', 'value'),
     Input('dropdown-dirs-a', 'value'),
     Input('dropdown-ports-si', 'value')])
def update_dropdown_industries(sector, directory, port):
    if sector is not None and not df_sector_ind.empty and 'sector' in df_sector_ind.columns:
        df_filtered = df_sector_ind[df_sector_ind['sector'] == sector]
        
        # Cross filter by portfolio if selected
        if directory is not None:
            symbols = md.get_symbols_dir_or_port(directory=directory, port=port)
            df_filtered = df_filtered[df_filtered['symbol'].isin(symbols)]
            
        industries = sorted(list(df_filtered['industry'].dropna().unique()))
        return [{'label': i, 'value': i} for i in industries]
    else:
        return []

# Update table callback
@callback(
    Output('results-date-1', 'children'),
    Output('results-table-1', 'children'),
    Input('radio-ndays-range', 'value'),
    Input('radio-perc-or-mean', 'value'),
    Input('dropdown-dirs-a', 'value'),
    Input('dropdown-ports-si', 'value'),
    Input('dropdown-sector', 'value'),
    Input('dropdown-industry', 'value')
)
def update_table(opt_ndays_range, perc_or_mean, directory, port, sector, industry):
    ndays_range = pf.get_ndays_range(opt_ndays_range)
    if directory is not None:
        symbols = md.get_symbols_dir_or_port(directory=directory, port=port)
    else:
        symbols = md.get_symbols(md.all)
    
    df_all = pf.df_secind_sym_perf(ndays_range, symbols)

    if sector is None:
        df = df_all
    elif sector is not None and industry is None:
        if 'sector' in df_all.columns:
            df = df_all[df_all['sector'] == sector]
        else:
            df = df_all
    elif sector is not None and industry is not None:
        if 'industry' in df_all.columns:
            df = df_all[df_all['industry'] == industry]
        else:
            df = df_all

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
                        'textAlign': 'left',
                        'maxWidth': '250px'
                    }
                ],
                sort_action='native'
            )
    )

# Robust Double-Click Event Listener (immune to column shifting)
@callback(Output("event-1", "children"), Input("el", "event"))
def click_event(event):
    if not event:
        raise PreventUpdate

    # Ensure it's inside a table cell and grab the text
    class_name = event.get("srcElement.className", "")
    if "dash-cell" in class_name:
        inner_text = event.get("srcElement.innerText", "").strip()
        
        # Verify the text matches standard Symbol format (1-5 uppercase letters, optional hyphen)
        if re.match(r"^[A-Z\-]{1,5}$", inner_text):
            webbrowser.open('https://seekingalpha.com/symbol/' + inner_text)
            
    return dash.no_update
