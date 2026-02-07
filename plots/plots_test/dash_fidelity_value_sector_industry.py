#!/usr/bin/env python3
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
from pymongo import MongoClient
import market_data as md
import apis
# 2. Initialize MongoDB (Using your module settings)
client = MongoClient()
db = client[md.db_client]

# 3. Setup Dash App
app = dash.Dash(__name__)


# --- DATA PROCESSING FUNCTION ---
def fetch_portfolio_data():
    """
    Combines the logic from your notebook cells to
    return a single merged dataframe.
    """
    # Get symbols from your directory
    directory = 'Holding'
    symbols = md.get_symbols_directory_and_port(directory=directory)

    # Get latest date from MongoDB
    collection = db[md.db_fidel_pos]
    unique_dates = sorted(collection.distinct("Date"), reverse=True)
    target_date = unique_dates[0]

    # Fetch current values
    query = {"Date": target_date, "Symbol": {"$in": symbols}}
    mdb_data = collection.find(query)
    df_current_value = md.mdb_to_df(mdb_data)[['Symbol', 'Current Value']]

    # Fetch Sector/Industry profiles using your apis module
    fields = ['sectorname', 'primaryname', 'symbol']
    df_sector_ind = apis.df_symbol_profile(symbols, fields)
    df_sector_ind.dropna(inplace=True)
    df_sector_ind.rename(columns={
        'symbol': 'Symbol',
        'sectorname': 'Sector',
        'primaryname': 'Industry'
    }, inplace=True)

    # Merge datasets
    df_merged = df_sector_ind.merge(df_current_value, on=['Symbol'], how='outer')
    return df_merged


# --- DASH LAYOUT ---
app.layout = html.Div([
    html.H1("Portfolio Sector & Industry Analysis", style={'textAlign': 'center'}),

    # Hidden Store to hold data in the browser (prevents over-querying MongoDB)
    dcc.Store(id='portfolio-storage'),

    # Chart Section
    html.Div([
        html.Div([
            dcc.Graph(id='sector-pie')
        ], style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='industry-pie')
        ], style={'width': '49%', 'display': 'inline-block'})
    ]),

    # Industry Table Section
    html.Div([
        html.H3(id='table-title', style={'paddingTop': '20px'}),
        dash_table.DataTable(
            id='industry-symbol-table',
            columns=[
                {"name": "Industry", "id": "Industry"},
                {"name": "Symbols", "id": "Symbol"},
                {"name": "Total Value", "id": "Current Value", "type": "numeric", "format": {"specifier": "$,.2f"}}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '12px',
                'font-family': 'sans-serif'
            },
            style_header={
                'backgroundColor': '#f4f4f4',
                'fontWeight': 'bold',
                'border': '1px solid black'
            },
            sort_action="native"
        )
    ], style={'width': '95%', 'margin': 'auto'})
], style={'font-family': 'sans-serif'})


# --- CALLBACKS ---

# 1. Fetch data from MongoDB once when the page loads
@app.callback(
    Output('portfolio-storage', 'data'),
    Input('sector-pie', 'id')
)
def load_initial_data(_):
    df = fetch_portfolio_data()
    return df.to_dict('records')


# 2. Update Sector Pie Chart
@app.callback(
    Output('sector-pie', 'figure'),
    Input('portfolio-storage', 'data')
)
def update_sector_chart(data):
    if not data: return {}
    df = pd.DataFrame(data)
    df_sector = df.groupby(['Sector'])['Current Value'].sum().reset_index()
    fig = px.pie(df_sector, values='Current Value', names='Sector',
                 title='Portfolio Value by Sector', hole=0.3 , color_discrete_sequence=px.colors.qualitative.Dark24)
    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
    return fig


# 3. Update Industry Pie Chart & Table based on Sector Click
@app.callback(
    [Output('industry-pie', 'figure'),
     Output('industry-symbol-table', 'data'),
     Output('table-title', 'children')],
    [Input('portfolio-storage', 'data'),
     Input('sector-pie', 'clickData')]
)
def update_industry_views(data, clickData):
    if not data: return {}, [], ""

    df = pd.DataFrame(data)

    # Determine which sector to filter by
    # (Defaults to 'Information Technology' as per your notebook logic)
    selected_sector = clickData['points'][0]['label'] if clickData else 'Information Technology'

    # Filter data for selected sector
    df_filtered = df[df['Sector'] == selected_sector]

    # Create Industry Pie Chart
    df_ind_pie = df_filtered.groupby(['Industry'])['Current Value'].sum().reset_index()
    fig_ind = px.pie(df_ind_pie, values='Current Value', names='Industry',
                     title=f'Industry Distribution: {selected_sector}', color_discrete_sequence=px.colors.qualitative.Dark24)
    fig_ind.update_traces(marker=dict(line=dict(color='#000000', width=2)))
    # Create the Grouped Table Logic you requested
    # Aggregates symbols into a list-string and sums values
    df_table_data = df_filtered.groupby('Industry').agg({
        'Symbol': lambda x: ', '.join(x.dropna().unique()),
        'Current Value': 'sum'
    }).reset_index()

    title = f"Symbols and Values for Sector: {selected_sector}"

    return fig_ind, df_table_data.to_dict('records'), title


# --- RUN SERVER ---
if __name__ == '__main__':
    # Using the 2026 'app.run' syntax
    app.run(debug=True, port=8050)
