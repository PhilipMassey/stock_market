import dash
from dash import dcc, html, dash_table, Input, Output, callback, register_page
import dash_daq as daq
from dash.dash_table.Format import Format, Scheme, Symbol
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pymongo import MongoClient
import market_data as md
import apis
import dash_bootstrap_components as dbc

register_page(__name__, path='/change-value-quantity')

# --- DATA PROCESSING ---

def load_portfolio_data(period=1):
    client = MongoClient()
    db = client[md.db_client]
    collection = db[md.db_fidel_pos]
    unique_dates = sorted(collection.distinct("Date"), reverse=True)

    if len(unique_dates) < period + 1:
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
        # Ensure Quantity exists, fill with 0 if not
        if 'Quantity' not in df.columns:
            df['Quantity'] = 0.0
        return df[['Date', 'Symbol', 'Current Value', 'Quantity']].set_index('Symbol')

    curr_vals = get_val_df(current_date)
    prev_vals = get_val_df(prev_date)

    if curr_vals.empty or prev_vals.empty:
        return pd.DataFrame(columns=['Sector', 'Symbol', 'Industry', 'Value Change', 'Quantity Change'])

    # Calculate Changes (Price Performance Logic)
    # Filter for common symbols (intersection)
    common_symbols = curr_vals.index.intersection(prev_vals.index)
    
    curr_common = curr_vals.loc[common_symbols]
    prev_common = prev_vals.loc[common_symbols]

    # Calculate Prices (Current Value / Quantity)
    curr_prices = curr_common['Current Value'] / curr_common['Quantity'].replace(0, pd.NA)
    prev_prices = prev_common['Current Value'] / prev_common['Quantity'].replace(0, pd.NA)

    # Value Change = (Current Price - Previous Price) * Current Quantity
    val_change_series = (curr_prices - prev_prices) * curr_common['Quantity']

    # Quantity Change
    qty_change_series = curr_common['Quantity'] - prev_common['Quantity']
    
    df_changes = pd.DataFrame({
        'Value Change': val_change_series,
        'Quantity Change': qty_change_series
    })

    df_changes = df_changes.dropna()
    df_changes.index.name = 'Symbol'
    df_changes = df_changes.reset_index()

    symbols = list(df_changes['Symbol'].values)
    fields = ['sectorname', 'primaryname', 'symbol']
    df_sector_ind = apis.df_symbol_profile(symbols, fields)
    df_sector_ind.dropna(inplace=True)
    df_sector_ind.rename(columns={'symbol': 'Symbol', 'sectorname': 'Sector', 'primaryname': 'Industry'}, inplace=True)

    df_master = df_sector_ind.merge(df_changes, on='Symbol', how='inner') # Inner join to only keep valid symbols
    return df_master.sort_values(by=['Sector', 'Symbol'])

# --- LAYOUT ---

layout = html.Div([
    html.H1("Portfolio Changes (Value & Quantity)",
            style={'textAlign': 'center', 'fontFamily': 'sans-serif', 'paddingTop': '20px'}),

    # Controls Section
    html.Div([
        html.Div([
            daq.ToggleSwitch(
                id='view-toggle-changes',
                label=['Negative Change', 'Positive Change'],
                labelPosition='bottom',
                value=True,  # Default to Positive Change
                color='#2c3e50'
            ),
        ], style={'display': 'inline-block', 'verticalAlign': 'middle', 'marginRight': '50px'}),

        html.Div([
            html.Label("Period (days): ", style={'marginRight': '10px', 'fontWeight': 'bold'}),
            dcc.Input(
                id='period-input-changes',
                type='number',
                value=1,
                min=1,
                step=1,
                style={'width': '80px'}
            )
        ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
    ], style={'padding': '20px', 'textAlign': 'center'}),

    dcc.Store(id='data-store-changes'),

    html.Div([
        dash_table.DataTable(
            id='changes-table',
            columns=[
                {"name": "Symbol", "id": "Symbol"},
                {"name": "Sector", "id": "Sector"},
                {"name": "Industry", "id": "Industry"},
                {
                    "name": "Value Change",
                    "id": "Value Change",
                    "type": "numeric",
                    "format": Format(precision=2, scheme=Scheme.fixed)
                },
                {
                    "name": "Quantity Change",
                    "id": "Quantity Change",
                    "type": "numeric",
                    "format": Format(precision=0, scheme=Scheme.fixed)
                }
            ],
            sort_action="native",
            style_table={'overflowX': 'auto', 'width': '80%', 'margin': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '12px', 'fontFamily': 'sans-serif'},
            style_header={'backgroundColor': '#f4f4f4', 'fontWeight': 'bold'}
        )
    ], style={'padding': '40px'})
])


# --- CALLBACKS ---

@callback(
    Output('data-store-changes', 'data'),
    Input('period-input-changes', 'value')
)
def update_data(period):
    if period is None:
        period = 1
    df = load_portfolio_data(period)
    return df.to_dict('records')

@callback(
    Output('changes-table', 'data'),
    [Input('view-toggle-changes', 'value'),
     Input('data-store-changes', 'data')]
)
def update_table(is_positive, data):
    if not data:
        return []
    
    df_master = pd.DataFrame(data)
    
    # Filter based on Value Change as per existing logic, or should it be OR logic?
    # Given the labels "Negative Change" / "Positive Change", usually refers to the primary metric "Value Change".
    
    if is_positive:
        # Show rows where Value Change is >= 0
        df_filtered = df_master[df_master['Value Change'] >= 0].copy()
    else:
        # Show rows where Value Change is < 0
        df_filtered = df_master[df_master['Value Change'] < 0].copy()
    
    # Rounding for display if not handled by DataTable format (DataTable handles it, but good to be clean)
    df_filtered['Value Change'] = df_filtered['Value Change'].round(2)
    df_filtered['Quantity Change'] = df_filtered['Quantity Change'].round(0)
    
    return df_filtered.to_dict('records')
