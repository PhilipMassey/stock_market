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
import dash_bootstrap_components as dbc

register_page(__name__, path='/fidelity-value-change-bar')

# --- DATA PROCESSING ---

def load_portfolio_data(period=1):
    client = MongoClient()
    db = client[md.db_client]
    collection = db[md.db_fidel_pos]
    unique_dates = sorted(collection.distinct("Date"), reverse=True)

    if len(unique_dates) < period + 1:
        # Handle case where not enough data
        current_date = unique_dates[0] if unique_dates else None
        prev_date = unique_dates[-1] if unique_dates else None
    else:
        current_date = unique_dates[0]
        prev_date = unique_dates[period]

    def get_val_df(a_date):
        if not a_date:
            return pd.DataFrame(columns=['Date', 'Symbol', 'Current Value', 'Quantity']).set_index('Symbol')
        query = {"Date": a_date}
        mdb_data = collection.find(query)
        df = md.mdb_to_df(mdb_data)
        if df.empty:
             return pd.DataFrame(columns=['Date', 'Symbol', 'Current Value', 'Quantity']).set_index('Symbol')
        if 'Quantity' not in df.columns:
            df['Quantity'] = 0.0
        return df[['Date', 'Symbol', 'Current Value', 'Quantity']].set_index('Symbol')

    curr_vals = get_val_df(current_date)
    prev_vals = get_val_df(prev_date)

    if curr_vals.empty or prev_vals.empty:
        return pd.DataFrame(columns=['Sector', 'Symbol', 'Industry', 'Value Change'])

    # Calculate Value Change logic
    # Filter for common symbols (intersection) to match previous behavior of dropping NaNs (new/sold positions)
    common_symbols = curr_vals.index.intersection(prev_vals.index)
    
    curr_common = curr_vals.loc[common_symbols]
    prev_common = prev_vals.loc[common_symbols]

    # Calculate Prices (Current Value / Quantity)
    # Handle division by zero or empty values implicitly by pandas, or explicit replace
    curr_prices = curr_common['Current Value'] / curr_common['Quantity'].replace(0, pd.NA)
    prev_prices = prev_common['Current Value'] / prev_common['Quantity'].replace(0, pd.NA)

    # Value Change = (Current Price - Previous Price) * Current Quantity
    # This removes the impact of buying/selling (Change in Quantity) 
    # and reflects the performance of the current holding.
    val_change_series = (curr_prices - prev_prices) * curr_common['Quantity']
    
    df_val_change = val_change_series.reset_index()
    df_val_change.columns = ['Symbol', 'Value Change']
    df_val_change = df_val_change.dropna()

    symbols = list(df_val_change['Symbol'].values)
    fields = ['sectorname', 'primaryname', 'symbol']
    df_sector_ind = apis.df_symbol_profile(symbols, fields)
    df_sector_ind.dropna(inplace=True)
    df_sector_ind.rename(columns={'symbol': 'Symbol', 'sectorname': 'Sector', 'primaryname': 'Industry'}, inplace=True)

    df_master = df_sector_ind.merge(df_val_change, on='Symbol', how='outer')
    return df_master.sort_values(by=['Sector', 'Symbol'])

# --- LAYOUT ---

layout = html.Div([
    html.H1("Portfolio Performance Drill-Down (Bar)",
            style={'textAlign': 'center', 'fontFamily': 'sans-serif', 'paddingTop': '20px'}),

    # Controls Section: Toggle Switch and Period Input
    html.Div([
        html.Div([
            daq.ToggleSwitch(
                id='view-toggle-bar',
                label=['Negative Change', 'Positive Change'],
                labelPosition='bottom',
                value=True,  # Default to Positive Change
                color='#2c3e50'
            ),
        ], style={'display': 'inline-block', 'verticalAlign': 'middle', 'marginRight': '50px'}),

        html.Div([
            html.Label("Period (days): ", style={'marginRight': '10px', 'fontWeight': 'bold'}),
            dcc.Input(
                id='period-input',
                type='number',
                value=1,
                min=1,
                step=1,
                style={'width': '80px'}
            )
        ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
    ], style={'padding': '20px', 'textAlign': 'center'}),

    # Store for data to share between callbacks
    dcc.Store(id='data-store'),

    html.Div([
        html.Div([dcc.Graph(id='sector-bar-chart')], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='industry-bar-chart')], style={'width': '48%', 'display': 'inline-block'})
    ]),

    html.Div([
        html.H3(id='table-title-bar', style={'textAlign': 'center'}),
        
        # Flex container for two tables
        html.Div([
            # Left Table: Industry Level
            html.Div([
                dash_table.DataTable(
                    id='symbol-table-bar',
                    columns=[
                        {"name": "Industry", "id": "Industry"},
                        {"name": "Symbols", "id": "Symbol"},
                        {
                            "name": "Total Value Change",
                            "id": "Value Change",
                            "type": "numeric",
                            "format": Format(precision=2, scheme=Scheme.fixed)
                        }
                    ],
                    sort_action="native",
                    row_selectable='single', # Enable selection
                    style_table={'overflowX': 'auto', 'width': '100%'},
                    style_cell={'textAlign': 'left', 'padding': '12px', 'fontFamily': 'sans-serif'},
                    style_header={'backgroundColor': '#f4f4f4', 'fontWeight': 'bold'}
                )
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),

            # Right Table: Symbol Detail Level
            html.Div([
                html.H4("Symbol Details", style={'textAlign': 'center'}),
                dash_table.DataTable(
                    id='symbol-detail-table',
                    columns=[
                        {"name": "Symbol", "id": "Symbol"},
                        {
                            "name": "Value Change",
                            "id": "Value Change",
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
    Output('data-store', 'data'),
    Input('period-input', 'value')
)
def update_data(period):
    if period is None:
        period = 1
    df = load_portfolio_data(period)
    return df.to_dict('records')

@callback(
    Output('sector-bar-chart', 'figure'),
    [Input('view-toggle-bar', 'value'),
     Input('data-store', 'data')]
)
def update_sector_chart(is_positive, data):
    if not data:
        return go.Figure()
    
    df_master = pd.DataFrame(data)
    
    # Logic for positive and negative splits
    if is_positive:
        df_plot = df_master[df_master['Value Change'] >= 0].copy()
    else:
        df_plot = df_master[df_master['Value Change'] < 0].copy()
    
    if df_plot.empty:
         return go.Figure()
    
    summary = df_plot.groupby('Sector')['Value Change'].sum().reset_index()
    title = f"{'Positive' if is_positive else 'Negative'} Change by Sector"

    # Use Bar chart
    # If negative, values are negative.
    fig = px.bar(
        summary, x='Sector', y='Value Change', title=title,
        color='Sector', # Color by Sector to be colorful
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig.update_layout(clickmode='event+select', showlegend=False)
    return fig


@callback(
    [Output('industry-bar-chart', 'figure'),
     Output('symbol-table-bar', 'data'),
     Output('table-title-bar', 'children'),
     Output('symbol-table-bar', 'selected_rows')], # Reset selection when filters change
    [Input('sector-bar-chart', 'clickData'),
     Input('view-toggle-bar', 'value'),
     Input('data-store', 'data')]
)
def update_industry_and_table(clickData, is_positive, data):
    if not data:
        return go.Figure(), [], "Loading...", []

    df_master = pd.DataFrame(data)

    if is_positive:
        source_df = df_master[df_master['Value Change'] >= 0].copy()
    else:
        source_df = df_master[df_master['Value Change'] < 0].copy()

    if not clickData:
        return go.Figure(), [], "Select a Sector bar to see details", []

    # For bar chart, the x value is the category (Sector)
    selected_sector = clickData['points'][0]['x']
    
    df_filtered = source_df[source_df['Sector'] == selected_sector]

    if df_filtered.empty:
        return go.Figure(), [], f"No details for Sector: {selected_sector}", []

    # Industry Bar
    ind_summary = df_filtered.groupby('Industry')['Value Change'].sum().reset_index()
    
    fig_ind = px.bar(
        ind_summary, x='Industry', y='Value Change',
        title=f"Industries in {selected_sector}",
        color='Industry',
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig_ind.update_layout(showlegend=False)

    # Aggregation for the table: List symbols and sum values
    table_df = df_filtered.groupby('Industry').agg({
        'Symbol': ', '.join,
        'Value Change': 'sum'
    }).reset_index()

    # Ensure decimals are rounded for the table
    table_df['Value Change'] = table_df['Value Change'].round(2)

    return fig_ind, table_df.to_dict('records'), f"Details for Sector: {selected_sector}", []


@callback(
    Output('symbol-detail-table', 'data'),
    [Input('symbol-table-bar', 'selected_rows'),
     State('symbol-table-bar', 'data'),
     Input('data-store', 'data')] 
)
def update_symbol_detail_table(selected_rows, industry_table_data, data):
    if not selected_rows or not industry_table_data or not data:
        return []
    
    # Get the selected industry from the row index
    row_idx = selected_rows[0]
    if row_idx >= len(industry_table_data):
        return []
    
    selected_industry = industry_table_data[row_idx]['Industry']
    
    # Filter the full dataset for this industry
    df_master = pd.DataFrame(data)
    df_symbols = df_master[df_master['Industry'] == selected_industry].copy()
    
    # Sort and format
    df_symbols = df_symbols[['Symbol', 'Value Change']]
    df_symbols['Value Change'] = df_symbols['Value Change'].round(2)
    
    return df_symbols.to_dict('records')
