import dash
from dash import dcc, html, dash_table, Input, Output, callback, register_page, State
import dash_daq as daq
from dash.dash_table.Format import Format, Scheme, Symbol
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pymongo import MongoClient
import market_data as md
import apis

register_page(__name__, path='/fidelity-value-sector-industry')

# --- DATA PROCESSING ---

def load_portfolio_data():
    client = MongoClient()
    db = client[md.db_client]
    collection = db[md.db_fidel_pos]
    unique_dates = sorted(collection.distinct("Date"), reverse=True)

    if not unique_dates:
        return pd.DataFrame(columns=['Sector', 'Symbol', 'Industry', 'Total Value'])

    current_date = unique_dates[0]

    def get_val_df(a_date):
        if not a_date:
            return pd.DataFrame(columns=['Date', 'Symbol', 'Current Value']).set_index('Symbol')
        query = {"Date": a_date}
        mdb_data = collection.find(query)
        df = md.mdb_to_df(mdb_data)
        if df.empty:
             return pd.DataFrame(columns=['Date', 'Symbol', 'Current Value']).set_index('Symbol')
        return df[['Date', 'Symbol', 'Current Value']].set_index('Symbol')

    curr_vals = get_val_df(current_date)

    if curr_vals.empty:
        return pd.DataFrame(columns=['Sector', 'Symbol', 'Industry', 'Total Value'])

    # Use Current Value directly
    df_curr_val = curr_vals[['Current Value']].reset_index()
    df_curr_val.columns = ['Symbol', 'Total Value']
    df_curr_val = df_curr_val.dropna()

    symbols = list(df_curr_val['Symbol'].values)
    fields = ['sectorname', 'primaryname', 'symbol']
    df_sector_ind = apis.df_symbol_profile(symbols, fields)
    df_sector_ind.dropna(inplace=True)
    df_sector_ind.rename(columns={'symbol': 'Symbol', 'sectorname': 'Sector', 'primaryname': 'Industry'}, inplace=True)

    df_master = df_sector_ind.merge(df_curr_val, on='Symbol', how='inner')
    return df_master.sort_values(by=['Sector', 'Symbol'])


# Load data at startup
df_portfolio_value = load_portfolio_data()

def create_sector_fig(directory=None, port=None):
    if directory is not None:
        symbols = md.get_symbols_dir_or_port(directory=directory, port=port)
        df_filtered = df_portfolio_value[df_portfolio_value['Symbol'].isin(symbols)]
    else:
        df_filtered = df_portfolio_value

    if df_filtered.empty:
        return go.Figure()
    
    summary = df_filtered.groupby('Sector')['Total Value'].sum().reset_index()
    title = "Total Value by Sector"

    fig = px.pie(
        summary, values='Total Value', names='Sector', title=title,
        color_discrete_sequence=px.colors.qualitative.Dark24, hole=0.3
    )
    # Requested styling: black border width 2
    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
    fig.update_layout(clickmode='event+select')
    return fig

# --- LAYOUT ---
dirs = md.get_portfolio_dirs()
dropdowns_ports = html.Div([
    html.Div([
        html.Label('Portfolio Directories'),
        dcc.Dropdown(id='dropdown-dirs-siv', options=[{'label': i, 'value': i} for i in dirs], value=None)],
        style={'width': '49%', 'float': 'left'}
    ),
    html.Div([
        html.Label('Portfolios'),
        dcc.Dropdown(id='dropdown-ports-siv', options=[], value=None)],
        style={'width': '49%', 'float': 'right'}
    ),
], style={'width': '100%', 'display': 'inline-block'})

layout = html.Div([
    html.H3("Portfolio Sector Value",
            style={'textAlign': 'center', 'fontFamily': 'sans-serif', 'paddingTop': '20px', 'fontSize': '18px'}),
    dropdowns_ports,

    html.Div([
        html.Div([dcc.Graph(id='sector-pie-chart', figure=create_sector_fig())], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='industry-pie-chart')], style={'width': '48%', 'display': 'inline-block'})
    ], style={'paddingTop': '20px'}),

    html.Div([
        html.H3(id='table-title', style={'textAlign': 'center'}),
        
        # Flex container for two tables
        html.Div([
            # Left Table: Industry Level
            html.Div([
                dash_table.DataTable(
                    id='symbol-table',
                    columns=[
                        {"name": "Industry", "id": "Industry"},
                        {"name": "Symbols", "id": "Symbol"},
                        {
                            "name": "Total Value",
                            "id": "Total Value",
                            "type": "numeric",
                            "format": Format(precision=2, scheme=Scheme.fixed)
                        }
                    ],
                    sort_action="native",
                    row_selectable='single',
                    style_table={'overflowX': 'auto', 'width': '100%'},
                    style_cell={'textAlign': 'left', 'padding': '12px', 'fontFamily': 'sans-serif'},
                    style_header={'backgroundColor': '#f4f4f4', 'fontWeight': 'bold'}
                )
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),

            # Right Table: Symbol Detail Level
            html.Div([
                html.H4("Symbol Details", style={'textAlign': 'center'}),
                dash_table.DataTable(
                    id='symbol-detail-value-table',
                    columns=[
                        {"name": "Symbol", "id": "Symbol"},
                        {
                            "name": "Total Value",
                            "id": "Total Value",
                            "type": "numeric",
                            "format": Format(precision=2, scheme=Scheme.fixed)
                        }
                    ],
                    sort_action="native",
                    style_table={'overflowX': 'auto', 'width': '100%'},
                    style_cell={'textAlign': 'left', 'padding': '12px', 'fontFamily': 'sans-serif'},
                    style_header={'backgroundColor': '#f4f4f4', 'fontWeight': 'bold'}
                )
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})

        ], style={'width': '95%', 'margin': 'auto'})
        
    ], style={'padding': '40px'})
])


# --- CALLBACKS ---

@callback(
    Output('dropdown-ports-siv', 'options'),
    [Input('dropdown-dirs-siv', 'value')]
)
def update_dropdown_ports(value):
    if value is not None:
        df_port_symbols = md.get_dir_port_symbols(value)
        return [{'label': i, 'value': i} for i in sorted(df_port_symbols["portfolio"].unique())]
    return []

@callback(
    Output('sector-pie-chart', 'figure'),
    [Input('dropdown-dirs-siv', 'value'),
     Input('dropdown-ports-siv', 'value')]
)
def update_sector_chart_callback(directory, port):
    return create_sector_fig(directory, port)

@callback(
    [Output('industry-pie-chart', 'figure'),
     Output('symbol-table', 'data'),
     Output('table-title', 'children'),
     Output('symbol-table', 'selected_rows')],
    [Input('sector-pie-chart', 'clickData'),
     Input('dropdown-dirs-siv', 'value'),
     Input('dropdown-ports-siv', 'value')]
)
def update_industry_and_table(clickData, directory, port):
    if directory is not None:
        symbols = md.get_symbols_dir_or_port(directory=directory, port=port)
        df_filtered_port = df_portfolio_value[df_portfolio_value['Symbol'].isin(symbols)]
    else:
        df_filtered_port = df_portfolio_value

    if not clickData:
        return go.Figure(), [], "Select a Sector slice to see details", []

    selected_sector = clickData['points'][0]['label']
    df_filtered = df_filtered_port[df_filtered_port['Sector'] == selected_sector]

    if df_filtered.empty:
        return go.Figure(), [], f"No details for Sector: {selected_sector}", []

    # Industry Pie
    ind_summary = df_filtered.groupby('Industry')['Total Value'].sum().reset_index()
    fig_ind = px.pie(
        ind_summary, values='Total Value', names='Industry',
        title=f"Industries in {selected_sector}",
        color_discrete_sequence=px.colors.qualitative.Dark24, hole=0.3
    )
    fig_ind.update_traces(marker=dict(line=dict(color='#000000', width=2)))

    # Aggregation for the table: List symbols and sum values
    table_df = df_filtered.groupby('Industry').agg({
        'Symbol': ', '.join,
        'Total Value': 'sum'
    }).reset_index()

    # Ensure decimals are rounded for the table
    table_df['Total Value'] = table_df['Total Value'].round(2)

    return fig_ind, table_df.to_dict('records'), f"Details for Sector: {selected_sector}", []


@callback(
    Output('symbol-detail-value-table', 'data'),
    [Input('symbol-table', 'selected_rows'),
     State('symbol-table', 'data'),
     State('dropdown-dirs-siv', 'value'),
     State('dropdown-ports-siv', 'value')] 
)
def update_symbol_detail_table(selected_rows, industry_table_data, directory, port):
    if not selected_rows or not industry_table_data:
        return []
    
    # Get the selected industry from the row index
    row_idx = selected_rows[0]
    if row_idx >= len(industry_table_data):
        return []
    
    selected_industry = industry_table_data[row_idx]['Industry']
    
    # Filter the full dataset for this industry
    if directory is not None:
        symbols = md.get_symbols_dir_or_port(directory=directory, port=port)
        df_symbols = df_portfolio_value[
            (df_portfolio_value['Industry'] == selected_industry) & 
            (df_portfolio_value['Symbol'].isin(symbols))
        ].copy()
    else:
        df_symbols = df_portfolio_value[df_portfolio_value['Industry'] == selected_industry].copy()
    
    # Sort and format
    df_symbols = df_symbols[['Symbol', 'Total Value']]
    df_symbols['Total Value'] = df_symbols['Total Value'].round(2)
    
    return df_symbols.to_dict('records')
