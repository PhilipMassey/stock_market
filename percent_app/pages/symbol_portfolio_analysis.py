import dash
dash.register_page(__name__, path="/"+__name__)
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
import performance as pf

label_size = '10px'


results_date = html.Div('Current date',id='results-date-3',
                        style={'width': '100%', 'text-align': 'center','font-size':label_size})

label_symbols_or_perc = html.Label('Symbols or Mean', style={'font-size':label_size})
radio_symbols_or_perc = html.Div([
    dcc.RadioItems(
        id='radio-symbols-or-perc',
        options=[
            {'label': 'Symbols', 'value': pf.symbols_option},
            {'label': 'Percentages', 'value': pf.perc_option}
            ],
       labelStyle={'display': 'block'},
       value=pf.symbols_option, ),
])
symbols_or_perc_block = html.Div([label_symbols_or_perc, radio_symbols_or_perc],
                                 style={'width': '33%', 'display': 'in-block', 'float': 'left'})


label_industry_sector = html.Label('Industry, Sector', style={'font-size':label_size})
radio_industry_sector = html.Div([
    dcc.RadioItems(
        id='radio-industry-sector',
        options=[
            {'label': 'Sector', 'value': analysis.sector_opt},
            {'label': 'Sector,Industry', 'value': analysis.sector_ind_opt},
            {'label': 'Symbols by Portfolio', 'value': 'symbols-by-portfolio'}
        ],
        labelStyle={'display': 'block'},
        value= 'sector',)
])
industry_sector_block = html.Div([label_industry_sector, radio_industry_sector],
                         style={'width': '33%', 'display': 'in-block', 'float': 'right'})


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
        value=pf.calc_percent_daily),
])
ndays_range_block = html.Div([label_ndays_range, radio_ndays_range],
                             style={'width': '33%', 'display': 'inline-block', 'float': 'right'})


dirs = md.get_portfolio_dirs()
dropdowns = html.Div([
        html.Div([
            html.Label('Portfolio Directories'),
            dcc.Dropdown(id='dropdown-dirs-1', options=[{'label': i, 'value': i} for i in dirs], value=None)],
            style={'width': '49%', 'float': 'left'}
            ),
    html.Div([
       html.Label('Portfolios'),
        dcc.Dropdown(id='dropdown-ports-1', options=[], value=None)],
        style = {'width': '49%','float': 'right'}
    ),

], style= {'width': '100%','display': 'inline-block'})

results_table = html.Div(id="results-table-2")

#layout = html.Div([results_date, radio_symbols_or_perc, radio_selection, dropdowns, results_table])
layout = html.Div([results_date, symbols_or_perc_block, industry_sector_block,
                   ndays_range_block, dropdowns,
                   results_table,
                   html.Div(id="event")
                   ])


#callback on directory selection
@callback(
    Output('dropdown-ports-1', 'options'),
    [Input('dropdown-dirs-1', 'value')])
def update_dropdown_ports(value):
    if(value != None):
        df_port_symbols = md.get_dir_port_symbols(value)
        return [{'label': i, 'value': i} for i in sorted(df_port_symbols["portfolio"].unique())]
    else:
        return []


@callback(
    Output('results-date-3', 'children'),
    Output('results-table-2', 'children'),
    Input('radio-symbols-or-perc', 'value'),
    Input('radio-industry-sector', 'value'),
    Input('radio-ndays-range', 'value'),
    Input('dropdown-dirs-1', 'value'),
    Input('dropdown-ports-1', 'value')
)
def update_table(radio_sym_mean, radio_ind_sec, opt_ndays_range,directory, port):
    ndays_range = pf.get_ndays_range(opt_ndays_range)
    if directory == None or len(directory) == 0:
        df = pd.DataFrame({'Status': ['depends']})
    else:
        symbols = md.get_symbols_dir_or_port(directory=directory, port=port)
        if radio_ind_sec == analysis.sector_opt:
            df = analysis.df_symbols_by_sector(symbols)
            if radio_sym_mean == pf.perc_option:
                analysis.assign_count_sum_mean(df, ndays_range)
                #df = df[['Sector', 'Count', 'Total %', 'Mean %']]
        elif radio_ind_sec == analysis.sector_ind_opt:
            df = analysis.df_symbols_by_sector_industry(symbols)
            if radio_sym_mean == pf.perc_option:
                analysis.assign_count_sum_mean(df, ndays_range)
                #df = df[['Sector', 'Industry', 'Count', 'Total %', 'Mean %']]

    return (md.get_date_for_ndays(0),
             dt.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                 export_format="csv",
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
