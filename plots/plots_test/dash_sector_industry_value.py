import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from pymongo import MongoClient

# 1. Leverage your local modules
import market_data as md
import apis

# Initialize DB connection once
client = MongoClient()
db = client[md.db_client]

app = dash.Dash(__name__)


# --- DATA LOGIC (Modified from your Notebook) ---

def fetch_portfolio_data():
    """Consolidates your logic from cells [27] through [31]"""
    directory = 'Holding'
    symbols = md.get_symbols_directory_and_port(directory=directory)

    collection = db[md.db_fidel_pos]
    latest_date = sorted(collection.distinct("Date"), reverse=True)[0]

    # Get current values
    query = {"Date": latest_date, "Symbol": {"$in": symbols}}
    mdb_data = collection.find(query)
    df_current_value = md.mdb_to_df(mdb_data)[['Symbol', 'Current Value']]

    # Get Sector/Industry mapping
    fields = ['sectorname', 'primaryname', 'symbol']
    df_sector_ind = apis.df_symbol_profile(symbols, fields)
    df_sector_ind.dropna(inplace=True)
    df_sector_ind.rename(columns={'symbol': 'Symbol', 'sectorname': 'Sector', 'primaryname': 'Industry'}, inplace=True)

    # Merge
    return df_sector_ind.merge(df_current_value, on=['Symbol'], how='outer')


# --- LAYOUT (The Web Page Structure) ---

app.layout = html.Div([
    html.H1("Portfolio Analytics Dashboard"),

    html.Div([
        # Left: Sector Pie Chart
        html.Div([
            dcc.Graph(id='sector-pie')
        ], style={'width': '48%', 'display': 'inline-block'}),

        # Right: Industry Pie Chart (Reactive to Sector Selection)
        html.Div([
            html.Label("Filter Industry by Sector Click:"),
            dcc.Graph(id='industry-pie')
        ], style={'width': '48%', 'display': 'inline-block'})
    ]),

    # Hidden store to keep data in memory without re-querying MongoDB too often
    dcc.Store(id='portfolio-storage')
])


# --- CALLBACKS (The Interactivity) ---

@app.callback(
    Output('portfolio-storage', 'data'),
    Input('sector-pie', 'id')  # Loads once on page start
)
def load_data(_):
    df = fetch_portfolio_data()
    return df.to_dict('records')


@app.callback(
    Output('sector-pie', 'figure'),
    Input('portfolio-storage', 'data')
)
def update_sector_chart(data):
    df = pd.DataFrame(data)
    df_sector = df.groupby(['Sector'])['Current Value'].sum().reset_index()
    fig = px.pie(df_sector, values='Current Value', names='Sector',
                 title='Value Distribution by Sector', hole=0.3)
    return fig


@app.callback(
    Output('industry-pie', 'figure'),
    [Input('portfolio-storage', 'data'),
     Input('sector-pie', 'clickData')]  # Logic from cell [39]
)
def update_industry_chart(data, clickData):
    df = pd.DataFrame(data)

    # Default to 'Information Technology' per your notebook,
    # or filter by what the user clicks on the first chart
    selected_sector = 'Information Technology'
    if clickData:
        selected_sector = clickData['points'][0]['label']

    df_sub = df[df['Sector'] == selected_sector]
    df_ind = df_sub.groupby(['Industry'])['Current Value'].sum().reset_index()

    fig = px.pie(df_ind, values='Current Value', names='Industry',
                 title=f'Industries in {selected_sector}')
    return fig

if __name__ == '__main__':
    app.run(debug=True)

