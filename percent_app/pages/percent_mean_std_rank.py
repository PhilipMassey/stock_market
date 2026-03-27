import dash
from dash import callback
from dash import html
from dash import dcc
from dash import dash_table as dt
from dash.dash_table.Format import Format, Scheme, Symbol
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

results_date = html.Div('Current date', id='results-date-rank',
                        style={'width': '100%', 'text-align': 'center', 'font-size': label_size})

label_perc_or_mean = html.Label('Perc or Mean', style={'font-size': label_size})
radio_perc_or_mean = html.Div([
    dcc.RadioItems(
        id='radio-perc-or-mean-rank',
        options=[
            {'label': 'Portfolio Mean', 'value': pf.mean_option},
            {'label': 'Symbol percent change', 'value': pf.perc_option}
        ],
        labelStyle={'display': 'block'},
        value=pf.perc_option,
    ),
])

label_ndays_range = html.Label('Select Period', style={'font-size': label_size})
def get_period_label(name, opt_val):
    try:
        ndays_range = pf.get_ndays_range(opt_val)
        date_newest = md.get_date_for_ndays(ndays_range[-1])
        date_oldest = md.get_date_for_ndays(ndays_range[0])
        return f"{name} ({date_oldest} to {date_newest})"
    except Exception:
        return name

perc_or_mean_block = html.Div([label_perc_or_mean, radio_perc_or_mean],
                              style={'width': '33%', 'display': 'inline-block'})

dirs = md.get_portfolio_dirs()
dropdowns_ports = html.Div([
    html.Div([
        html.Label('Portfolio Directories'),
        dcc.Dropdown(id='dropdown-dirs-rank', options=[{'label': i, 'value': i} for i in dirs], value=None)],
        style={'width': '49%', 'float': 'left'}
    ),
    html.Div([
        html.Label('Portfolios'),
        dcc.Dropdown(id='dropdown-ports-rank', options=[], value=None)],
        style={'width': '49%', 'float': 'right'}
    ),
], style={'width': '100%', 'display': 'inline-block'})


if hasattr(md, 'df_sector_ind'):
    df_sector_ind = md.df_sector_ind
elif hasattr(md, 'get_sector_data'):
    df_sector_ind = md.get_sector_data()
else:
    df_sector_ind = pd.DataFrame()

if not df_sector_ind.empty and 'sector' in df_sector_ind.columns:
    sectors = sorted(list(df_sector_ind['sector'].unique()))
else:
    sectors = []

dropdowns_sectors = html.Div([
    html.Div([
        html.Label('Sector'),
        dcc.Dropdown(id='dropdown-sector-rank', options=[{'label': i, 'value': i} for i in sectors], value=None)],
        style={'width': '49%', 'float': 'left'}
    ),
    html.Div([
        html.Label('Industry'),
        dcc.Dropdown(id='dropdown-industry-rank', options=[], value=None)],
        style={'width': '49%', 'float': 'right'}
    ),
], style={'width': '100%', 'display': 'inline-block'})

results_table = html.Div(id="results-table-rank")
listen_table = html.Div(
    [
        EventListener(
            id="el-rank",
            events=[{"event": "dblclick", "props": ["srcElement.className", "srcElement.innerText"]}],
            logging=True,
            children=results_table,
        )
    ]
)

dct_profile = apis.dct_mdb_symbol_names()

def get_tooltip(symbol):
    line = 'No profile'
    if symbol in dct_profile:
        line = dct_profile[symbol]
    if line is None or pd.isna(line):
        line = 'No profile'
    return str(line)

def serve_layout():
    radio_ndays_range = html.Div([
        dcc.RadioItems(
            id='radio-ndays-range-rank',
            options=[
                {'label': get_period_label('2 Months', pf.calc_percent_2monthly), 'value': pf.calc_percent_2monthly},
                {'label': get_period_label('1 Month', pf.calc_percent_monthly), 'value': pf.calc_percent_monthly},
                {'label': get_period_label('2 Weeks', pf.calc_percent_2weekly), 'value': pf.calc_percent_2weekly},
                {'label': get_period_label('1 Week', pf.calc_percent_weekly), 'value': pf.calc_percent_weekly},
                {'label': get_period_label('Daily', pf.calc_percent_daily), 'value': pf.calc_percent_daily}
            ],
            labelStyle={'display': 'block'},
            value=pf.calc_percent_daily),
    ])
    ndays_range_block = html.Div([label_ndays_range, radio_ndays_range],
                                 style={'width': '33%', 'display': 'inline-block'})

    return html.Div([
        html.H3("Percent Mean & Std Rank", style={'textAlign': 'center', 'fontFamily': 'sans-serif', 'paddingTop': '20px', 'fontSize': '18px'}),
        results_date, perc_or_mean_block, ndays_range_block,
        dropdowns_ports, dropdowns_sectors,
        listen_table,
        html.Div(id="event-rank")
    ])

layout = serve_layout

dash.register_page(__name__, path="/"+__name__)

@callback(
    Output('dropdown-ports-rank', 'options'),
    [Input('dropdown-dirs-rank', 'value')]
)
def update_dropdown_ports(value):
    if value is not None:
        df_port_symbols = md.get_dir_port_symbols(value)
        return [{'label': i, 'value': i} for i in sorted(df_port_symbols["portfolio"].unique())]
    return []

@callback(
    Output('dropdown-industry-rank', 'options'),
    [Input('dropdown-sector-rank', 'value')]
)
def update_dropdown_industries(value):
    if value is not None and not df_sector_ind.empty and 'sector' in df_sector_ind.columns:
        try:
            industries = sorted(list(df_sector_ind[df_sector_ind['sector'] == value]['industry'].unique()))
            return [{'label': i, 'value': i} for i in industries]
        except Exception:
            return []
    return []

@callback(
    Output('results-date-rank', 'children'),
    Output('results-table-rank', 'children'),
    Input('radio-ndays-range-rank', 'value'),
    Input('radio-perc-or-mean-rank', 'value'),
    Input('dropdown-dirs-rank', 'value'),
    Input('dropdown-ports-rank', 'value'),
    Input('dropdown-sector-rank', 'value'),
    Input('dropdown-industry-rank', 'value')
)
def update_table(opt_ndays_range, perc_or_mean, directory, port, sector, industry):
    import scipy.stats as stats
    results_date_value = 'No results'
    ndays_range = pf.get_ndays_range(opt_ndays_range)
    if directory is not None:
        symbols = md.get_symbols_dir_or_port(directory=directory, port=port)
    else:
        symbols = md.get_symbols(md.all)
        
    df_all = pf.df_secind_sym_perf(ndays_range, symbols)
    
    # Calculate new metrics
    ind_mean_pc = df_all.groupby(['sector', 'industry'])['over_pc'].transform('mean')
    df_all['rel_strength_ind'] = df_all['over_pc'] - ind_mean_pc

    mask_std_gt_0 = df_all['pc_std'] > 0
    df_all['prob_green_day_%'] = 0.0
    df_all.loc[mask_std_gt_0, 'prob_green_day_%'] = stats.norm.sf(0, loc=df_all.loc[mask_std_gt_0, 'pc_mean'], scale=df_all.loc[mask_std_gt_0, 'pc_std']) * 100
    
    df_all['stretch_score'] = 0.0
    df_all.loc[mask_std_gt_0, 'stretch_score'] = df_all.loc[mask_std_gt_0, 'over_pc'] / df_all.loc[mask_std_gt_0, 'pc_std']
    
    df_all['kelly_fraction'] = 0.0
    df_all.loc[mask_std_gt_0, 'kelly_fraction'] = df_all.loc[mask_std_gt_0, 'pc_mean'] / (df_all.loc[mask_std_gt_0, 'pc_std'] ** 2)

    # Calculate rank for each measure.
    df_all['risk_reward_rank'] = df_all['risk_reward'].rank(ascending=False, method='min')
    df_all['rel_strength_ind_rank'] = df_all['rel_strength_ind'].rank(ascending=False, method='min')
    df_all['prob_green_day_rank'] = df_all['prob_green_day_%'].rank(ascending=False, method='min')
    df_all['stretch_score_rank'] = df_all['stretch_score'].rank(ascending=False, method='min')
    df_all['kelly_fraction_rank'] = df_all['kelly_fraction'].rank(ascending=False, method='min')

    if sector is None:
        df = df_all
    elif sector is not None and industry is None:
        df = df_all[df_all['sector'] == sector]
    elif sector is not None and industry is not None:
        df = df_all[df_all['industry'] == industry]

    rename_dict = {
        'sector': 'Sector', 'industry': 'Industry', 'symbol': 'Symbol', 
        'over_pc': 'Over PC', 'pc_mean': 'PC Mean', 'pc_std': 'PC Std',
        'risk_reward_rank': 'Risk Reward Rank',
        'rel_strength_ind_rank': 'Rel Strength Rank', 'prob_green_day_rank': 'Prob Green Rank',
        'stretch_score_rank': 'Stretch Score Rank', 'kelly_fraction_rank': 'Kelly Rank'
    }
    
    # Only keep the specific columns and rename them
    df = df[list(rename_dict.keys())].copy()
    df.rename(columns=rename_dict, inplace=True)

    perc_fmt = Format(precision=2, scheme=Scheme.fixed, symbol=Symbol.yes, symbol_suffix='%')
    rank_fmt = Format(precision=0, scheme=Scheme.fixed)
    
    formatted_columns = []
    for i in df.columns:
        col = {"name": i, "id": i}
        if i in ['Over PC', 'PC Mean', 'PC Std']:
            col["type"] = "numeric"
            col["format"] = perc_fmt
        elif 'Rank' in i:
            col["type"] = "numeric"
            col["format"] = rank_fmt
        formatted_columns.append(col)

    tooltip_data = [
        {
            'Symbol': {'value': get_tooltip(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in df[['Symbol']].to_dict('records')
    ]

    return (
        md.get_date_for_ndays(ndays_range[-1]),
        dt.DataTable(
            id='table-rank',
            columns=formatted_columns,
            tooltip_data=tooltip_data,
            data=df.to_dict('records'),
            export_format="csv",
            style_cell={
                'font_family': 'arial',
                'font_size': '20px',
                'text_align': 'right'
            },
            style_cell_conditional=[
                {'if': {'column_id': 'Symbol'}, 'textAlign': 'left'},
                {'if': {'column_id': 'Sector'}, 'textAlign': 'left'},
                {'if': {'column_id': 'Industry'}, 'textAlign': 'left'},
                {'if': {'column_id': 'Symbol'}, 'maxWidth': '250px'},
            ],
            sort_action='native',
            sort_by=[{'column_id': 'Risk Reward Rank', 'direction': 'asc'}] if 'Risk Reward Rank' in df.columns else []
        )
    )

@callback(Output("event-rank", "children"), Input("el-rank", "event"), Input("el-rank", "n_events"))
def click_event(event, n_events):
    if not event or "cell--selected" not in event.get("srcElement.className", ""):
        raise PreventUpdate

    if event["srcElement.className"] == 'dash-cell column-2 cell--selected focused':
        symbol = event['srcElement.innerText']
        webbrowser.open('https://seekingalpha.com/symbol/' + symbol)
