import dash
from dash import callback, dcc, html, Input, Output, dash_table as dt
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
import pandas as pd
import market_data as md

dash.register_page(__name__)

def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Symbol Filter", className="mb-4"),
                dcc.Input(
                    id="input-symbol",
                    type="text",
                    placeholder="Enter Symbol (e.g., AAPL)",
                    debounce=True,
                    className="search-input mb-4"
                )
            ], width=12, md=6, lg=4)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='output-symbol'), width=12, className="mb-2")
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='listing-table'), width=12, className="mb-4")
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='details-table'), width=12)
        ])
    ], fluid=True, className="py-4")


def get_symbol_data(symbol):
    """Fetches detailed data for a given symbol."""
    db_coll_name = 'symbol_info'
    # Optimize query by selecting only necessary fields if possible, 
    # currently keeping original 'fields' list for compatibility.
    ndays = 0
    period = 1000
    symbols = [symbol]
    
    fields = [
        'Date', 'symbol', 'divYield', 'eps', 'estimateEps', 'evEbit', 'evEbitda', 
        'evFcf', 'evSales', 'fcf', 'fcfShare', 'ltDebtCap', 'marketCap', 
        'movAvg10d', 'movAvg10w', 'movAvg200d', 'payout4y', 'payoutRatio', 
        'pegRatio', 'peRatioFwd', 'priceBook', 'priceCf', 'priceSales', 
        'priceTangb', 'quickRatio', 'revenueGrowth', 'revenueGrowth3', 
        'roa', 'roe', 'shares', 'shortIntPctFloat', 'volume'
    ]
    
    try:
        df = md.df_mdb_between_days(ndays, period, symbols, db_coll_name, fields)
        if df.empty:
            return pd.DataFrame()
            
        df.index = df.index.strftime('%m/%d/%Y')
        df = df.T
        df.reset_index(inplace=True)
        df = df.rename(columns={'index': 'Date'})
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

@callback(
    Output('output-symbol', 'children'),
    Output('listing-table', 'children'),
    Output('details-table', 'children'),
    Input('input-symbol', 'value')
)
def update_table(symbol):
    if not symbol:
        return "", "", ""
    
    symbol = symbol.upper()
    
    # Fetch data fresh inside callback
    try:
        holding_df = md.get_port_and_symbols('Holding')
        if not holding_df.empty:
            holding_portfolios = set(holding_df['portfolio'].unique())
        else:
            holding_portfolios = set()
            
        portfolios_symbols = md.get_port_and_symbols(directory=md.all)
        
        # Filter logic
        portfolios_with_symbols = portfolios_symbols[portfolios_symbols['symbol'] == symbol]['portfolio']
        
        dct = {
            'Listed': [port for port in portfolios_with_symbols if port not in holding_portfolios],
            'Holding': [port for port in portfolios_with_symbols if port in holding_portfolios]
        }
        
        dfp = pd.DataFrame.from_dict(dct, orient='index').T
        dfd = get_symbol_data(symbol)
        
    except Exception as e:
        return f"Error: {str(e)}", "", ""

    # Portfolio Listing Table
    listing_table = dt.DataTable(
        id='table-portfolio',
        columns=[{"name": i, "id": i} for i in dfp.columns],
        data=dfp.to_dict('records'),
        style_cell={'textAlign': 'center'},
        style_header={'fontWeight': 'bold'},
        sort_action='native',
        page_size=10
    )

    if dfd.empty:
        details_table = html.Div("No details found for this symbol.")
    else:
        # Symbol Details Table
        # Auto-detect numeric columns for formatting could be added here, 
        # but preserving original specific formatting for now.
        cols = []
        if len(dfd.columns) > 1:
            for col in dfd.columns:
                if col == dfd.columns[0]:
                    cols.append({"name": col, "id": col, "type": "any"})
                else:
                    cols.append({
                        "name": col, 
                        "id": col, 
                        "type": "numeric", 
                        "format": Format(scheme=Scheme.decimal_si_prefix, precision=3)
                    })
        
        details_table = dt.DataTable(
            id='table-details',
            columns=cols,
            data=dfd.to_dict('records'),
            style_cell={
                'textAlign': 'left', 
                'fontFamily': 'Arial, sans-serif'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            sort_action='native',
            page_size=20
        )

    return f"Displaying results for: {symbol}", listing_table, details_table


