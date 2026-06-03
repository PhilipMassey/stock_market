import dash
from dash import callback
from dash import html
from dash import dcc
from dash import dash_table as dt
from dash.dash_table.Format import Format, Scheme, Symbol
from dash.dependencies import Output, Input, State
import market_data as md
import performance as pf
import pandas as pd
from dash.exceptions import PreventUpdate
import datetime

dash.register_page(__name__, path="/"+__name__)

global_cache = {
    'date': None,
    'df_all_periods': None
}

def get_all_periods_ranked():
    import scipy.stats as stats
    today = datetime.datetime.now().strftime('%Y-%m-%d %H') # Cache per hour
    if global_cache['date'] == today and global_cache['df_all_periods'] is not None:
        return global_cache['df_all_periods']
    
    symbols = md.get_symbols(md.all)
    all_dfs = []
    periods = [
        ('Daily', pf.calc_percent_daily),
        ('1 Week', pf.calc_percent_weekly),
        ('2 Weeks', pf.calc_percent_2weekly),
        ('1 Month', pf.calc_percent_monthly),
        ('2 Months', pf.calc_percent_2monthly)
    ]
    
    for period_name, opt_val in periods:
        ndays_range = pf.get_ndays_range(opt_val)
        df_all = pf.df_secind_sym_perf(ndays_range, symbols)
        
        ind_mean_pc = df_all.groupby(['sector', 'industry'])['over_pc'].transform('mean')
        df_all['rel_strength_ind'] = df_all['over_pc'] - ind_mean_pc

        mask_std_gt_0 = df_all['pc_std'] > 0
        df_all['prob_green_day_%'] = 0.0
        df_all.loc[mask_std_gt_0, 'prob_green_day_%'] = stats.norm.sf(0, loc=df_all.loc[mask_std_gt_0, 'pc_mean'], scale=df_all.loc[mask_std_gt_0, 'pc_std']) * 100
        
        df_all['stretch_score'] = 0.0
        df_all.loc[mask_std_gt_0, 'stretch_score'] = df_all.loc[mask_std_gt_0, 'over_pc'] / df_all.loc[mask_std_gt_0, 'pc_std']
        
        df_all['kelly_fraction'] = 0.0
        df_all.loc[mask_std_gt_0, 'kelly_fraction'] = df_all.loc[mask_std_gt_0, 'pc_mean'] / (df_all.loc[mask_std_gt_0, 'pc_std'] ** 2)

        df_all['risk_reward_rank'] = df_all['risk_reward'].rank(ascending=False, method='min')
        df_all['rel_strength_ind_rank'] = df_all['rel_strength_ind'].rank(ascending=False, method='min')
        df_all['prob_green_day_rank'] = df_all['prob_green_day_%'].rank(ascending=False, method='min')
        df_all['stretch_score_rank'] = df_all['stretch_score'].rank(ascending=False, method='min')
        df_all['kelly_fraction_rank'] = df_all['kelly_fraction'].rank(ascending=False, method='min')

        df_all['Period'] = period_name
        date_newest = md.get_date_for_ndays(ndays_range[-1])
        date_oldest = md.get_date_for_ndays(ndays_range[0])
        df_all['Date Range'] = f"{date_oldest} to {date_newest}"

        all_dfs.append(df_all)

    df_concat = pd.concat(all_dfs, ignore_index=True)
    global_cache['date'] = today
    global_cache['df_all_periods'] = df_concat
    return df_concat

# Sectors logic
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
        html.Label('Sector', style={'font-size': '18px'}),
        dcc.Dropdown(id='dropdown-sector-symview', options=[{'label': i, 'value': i} for i in sectors], value=None)],
        style={'width': '32%', 'display': 'inline-block'}
    ),
    html.Div([
        html.Label('Industry', style={'font-size': '18px'}),
        dcc.Dropdown(id='dropdown-industry-symview', options=[], value=None)],
        style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%'}
    ),
    html.Div([
        html.Label('Sort Period', style={'font-size': '18px'}),
        dcc.Dropdown(id='dropdown-period-symview', options=[{'label': p, 'value': p} for p in ['Daily', '1 Week', '2 Weeks', '1 Month', '2 Months']], value='1 Month')],
        style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%'}
    ),
], style={'width': '100%', 'margin-bottom': '20px'})

dropdowns_ports = html.Div([
    html.Div([
        html.Label('Portfolio Directories', style={'font-size': '18px'}),
        dcc.Dropdown(id='dropdown-dirs-symview', options=[{'label': i, 'value': i} for i in md.get_portfolio_dirs()], value=None)],
        style={'width': '48%', 'display': 'inline-block'}
    ),
    html.Div([
        html.Label('Portfolios', style={'font-size': '18px'}),
        dcc.Dropdown(id='dropdown-ports-symview', options=[], value=None)],
        style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}
    ),
], style={'width': '100%', 'margin-bottom': '20px'})

table_1 = dt.DataTable(
    id='table-1-symbols',
    columns=[
        {'name': 'Sector', 'id': 'Sector'},
        {'name': 'Industry', 'id': 'Industry'},
        {'name': 'Symbol', 'id': 'Symbol'},
        {'name': 'Rank (Risk/Reward)', 'id': 'risk_reward_rank', 'type': 'numeric', 'format': Format(precision=0, scheme=Scheme.fixed)},
        {'name': 'Rank (Rel Strength)', 'id': 'rel_strength_ind_rank', 'type': 'numeric', 'format': Format(precision=0, scheme=Scheme.fixed)},
        {'name': 'Rank (Stretch)', 'id': 'stretch_score_rank', 'type': 'numeric', 'format': Format(precision=0, scheme=Scheme.fixed)},
        {'name': 'Rank (Kelly)', 'id': 'kelly_fraction_rank', 'type': 'numeric', 'format': Format(precision=0, scheme=Scheme.fixed)}
    ],
    data=[],
    row_selectable="single",
    sort_action="native",
    selected_rows=[],
    page_size=10,
    style_cell={
        'font_family': 'arial',
        'font_size': '20px',
        'text_align': 'left'
    }
)

table_2 = html.Div([
    html.H3(id='table-2-title', style={'margin-top': '40px', 'text-align': 'center'}),
    dt.DataTable(
        id='table-2-periods',
        columns=[],
        data=[],
        export_format='csv',
        style_cell={
            'font_family': 'arial',
            'font_size': '20px',
            'text_align': 'right'
        },
        style_cell_conditional=[
            {'if': {'column_id': 'Period'}, 'textAlign': 'left'},
            {'if': {'column_id': 'Date Range'}, 'textAlign': 'left'}
        ]
    )
])

def serve_layout():
    return html.Div([
        html.Div([
            html.Div([
                html.Label('Risk/Reward Rank Filter:', style={'font-size': '16px', 'font-weight': 'bold', 'marginRight': '10px', 'display': 'block', 'marginBottom': '10px'}),
                dcc.Slider(
                    id='slider-rank-filter',
                    min=1,
                    max=500,
                    step=1,
                    value=500,
                    marks={1: '1', 100: '100', 200: '200', 300: '300', 400: '400', 500: '500'},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={
                'width': '35%',
                'display': 'inline-block',
                'marginRight': '2%',
                'verticalAlign': 'top',
                'paddingTop': '10px',
                'paddingLeft': '10px',
                'paddingRight': '10px'
            }),
            html.Div([
                html.H3("Symbol Multi-Period Rank Viewer", style={'text-align': 'center', 'paddingTop': '0px', 'fontSize': '18px', 'margin': '0'})
            ], style={
                'width': '63%',
                'display': 'inline-block',
                'verticalAlign': 'top'
            })
        ], style={'width': '100%', 'paddingTop': '20px'}),
        dropdowns_ports,
        dcc.Loading(
            id="loading-1",
            type="circle",
            children=[
                dropdowns_sectors,
                html.Div(table_1, style={'margin-top': '20px'}),
                table_2
            ]
        ),
        html.Div(id="loading-div-dummy", style={'display': 'none'}) # Just to force loading state if needed
    ])

layout = serve_layout

@callback(
    Output('dropdown-industry-symview', 'options'),
    [Input('dropdown-sector-symview', 'value')]
)
def update_dropdown_industries(value):
    if value is not None and not df_sector_ind.empty and 'sector' in df_sector_ind.columns:
        industries = sorted(list(df_sector_ind[df_sector_ind['sector'] == value]['industry'].unique()))
        return [{'label': i, 'value': i} for i in industries]
    return []

@callback(
    Output('dropdown-ports-symview', 'options'),
    [Input('dropdown-dirs-symview', 'value')]
)
def update_dropdown_ports(value):
    if value is not None:
        df_port_symbols = md.get_dir_port_symbols(value)
        return [{'label': i, 'value': i} for i in sorted(df_port_symbols["portfolio"].unique())]
    return []

@callback(
    Output('table-1-symbols', 'data'),
    Output('table-1-symbols', 'selected_rows'),
    Input('dropdown-sector-symview', 'value'),
    Input('dropdown-industry-symview', 'value'),
    Input('dropdown-period-symview', 'value'),
    Input('dropdown-dirs-symview', 'value'),
    Input('dropdown-ports-symview', 'value'),
    Input('slider-rank-filter', 'value'),
    Input('loading-div-dummy', 'children') # Trigger on load to get full list initially
)
def update_symbol_table(sector, industry, period, directory, port, rank_filter_value, dummy):
    df_all = get_all_periods_ranked()
    
    if directory is not None:
        symbols = md.get_symbols_dir_or_port(directory=directory, port=port)
        df_all = df_all[df_all['symbol'].isin(symbols)]
        
    # Isolate specifically by the sorted period requested
    if period:
        df_period = df_all[df_all['Period'] == period]
    else:
        df_period = df_all[df_all['Period'] == '1 Month']
        
    df_unique = df_period[['sector', 'industry', 'symbol', 'risk_reward_rank', 'rel_strength_ind_rank', 'stretch_score_rank', 'kelly_fraction_rank']].copy()
    
    if sector is not None and industry is None:
        df_unique = df_unique[df_unique['sector'] == sector]
    elif sector is not None and industry is not None:
        df_unique = df_unique[df_unique['industry'] == industry]
    
    # Filter by rank slider value (rank must be <= selected value)
    if rank_filter_value is not None:
        df_unique = df_unique[df_unique['risk_reward_rank'] <= rank_filter_value]
        
    df_unique = df_unique.sort_values(by=['risk_reward_rank', 'sector', 'industry', 'symbol'])
    df_unique.rename(columns={'sector': 'Sector', 'industry': 'Industry', 'symbol': 'Symbol'}, inplace=True)
    return df_unique.to_dict('records'), []

@callback(
    Output('table-2-periods', 'data'),
    Output('table-2-periods', 'columns'),
    Output('table-2-title', 'children'),
    Input('table-1-symbols', 'selected_rows'),
    State('table-1-symbols', 'data')
)
def update_period_table(selected_rows, table_1_data):
    if not selected_rows or not table_1_data:
        return [], [], "Select a symbol to view its multi-period ranks"
        
    selected_idx = selected_rows[0]
    selected_symbol = table_1_data[selected_idx]['Symbol']
    
    df_all = get_all_periods_ranked()
    df_sym = df_all[df_all['symbol'] == selected_symbol].copy()
    
    rename_dict = {
        'Period': 'Period', 'Date Range': 'Date Range',
        'over_pc': 'Over PC', 'pc_mean': 'PC Mean', 'pc_std': 'PC Std',
        'risk_reward_rank': 'Risk Reward Rank', 'rel_strength_ind_rank': 'Rel Strength Rank',
        'prob_green_day_rank': 'Prob Green Rank', 'stretch_score_rank': 'Stretch Score Rank', 
        'kelly_fraction_rank': 'Kelly Rank'
    }
    
    df_sym = df_sym[list(rename_dict.keys())]
    df_sym.rename(columns=rename_dict, inplace=True)
    
    period_order = {'Daily': 1, '1 Week': 2, '2 Weeks': 3, '1 Month': 4, '2 Months': 5}
    df_sym['order'] = df_sym['Period'].map(period_order)
    df_sym.sort_values('order', inplace=True)
    df_sym.drop(columns=['order'], inplace=True)
    
    perc_fmt = Format(precision=2, scheme=Scheme.fixed, symbol=Symbol.yes, symbol_suffix='%')
    rank_fmt = Format(precision=0, scheme=Scheme.fixed)
    
    formatted_columns = []
    for i in df_sym.columns:
        col = {"name": i, "id": i}
        if i in ['Over PC', 'PC Mean', 'PC Std']:
            col["type"] = "numeric"
            col["format"] = perc_fmt
        elif 'Rank' in i:
            col["type"] = "numeric"
            col["format"] = rank_fmt
        formatted_columns.append(col)
        
    title = f"Rankings across Periods for {selected_symbol}"
    return df_sym.to_dict('records'), formatted_columns, title
