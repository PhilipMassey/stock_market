import dash
from dash import dcc, html, dash_table, Input, Output, callback, register_page
import dash_daq as daq
from dash.dash_table.Format import Format, Scheme, Symbol
import pandas as pd
from pymongo import MongoClient
import market_data as md
import apis
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

register_page(__name__, path='/change-value-quantity')

# --- DATA PROCESSING ---

def load_portfolio_data(start_date=None, end_date=None):
    from market_data.stock_mdb.mongo_connection_manager import get_mongo_database
    db = get_mongo_database(md.db_client)
    fidel_coll = db[md.db_fidel_pos]
    close_coll = db[md.db_close]
    
    if end_date is None:
        end_date = datetime.today()
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date[:10], '%Y-%m-%d')
        
    if start_date is None:
        start_date = end_date - timedelta(days=7)
    elif isinstance(start_date, str):
        start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')

    unique_close_dates = sorted(close_coll.distinct("Date"), reverse=True)
    if not unique_close_dates:
        return pd.DataFrame(), []
        
    def get_closest_trading_date(target):
        valid = [d for d in unique_close_dates if d <= target]
        return valid[0] if valid else unique_close_dates[-1]

    unique_fidel_dates = sorted(fidel_coll.distinct("Date"), reverse=True)
    
    # Filter dates natively within bounds (start_date to end_date)
    valid_fidel_dates = [d for d in unique_fidel_dates if start_date <= d <= end_date]
    if not valid_fidel_dates:
        return pd.DataFrame(), []

    all_symbols = set()
    date_dataframes = {}
    
    for fidel_date in valid_fidel_dates:
        fidel_date_str = fidel_date.strftime('%Y-%m-%d')
        
        # Pull Fidelity Qty
        fidel_data = fidel_coll.find({"Date": fidel_date})
        df_quantities = pd.DataFrame(list(fidel_data))
        if df_quantities.empty or 'Quantity' not in df_quantities.columns:
            continue
        df_quantities = df_quantities[['Symbol', 'Quantity']].set_index('Symbol')
        
        # Turn it into a nearest business date
        nearest_biz_date = get_closest_trading_date(fidel_date)
        close_doc = close_coll.find_one({"Date": nearest_biz_date})
        if not close_doc:
            continue
            
        ps_prices = pd.Series({k:v for k,v in close_doc.items() if k not in ['_id', 'Date', 'index']})

        # Calculate values dynamically
        common = df_quantities.index.intersection(ps_prices.index)
        all_symbols.update(common)
        
        qty = df_quantities.loc[common]['Quantity']
        prc = ps_prices[common].astype(float)
        val = qty * prc
        
        qty_col = f"Qty {fidel_date_str}"
        val_col = f"Val {fidel_date_str}"
        
        df_date = pd.DataFrame({
            qty_col: qty,
            val_col: val
        })
        date_dataframes[fidel_date_str] = df_date

    if not date_dataframes:
        return pd.DataFrame(), valid_fidel_dates
        
    # Compile master framework across all dates
    df_master = pd.DataFrame(index=list(all_symbols))
    for date_str, df_date in date_dataframes.items():
        df_master = df_master.join(df_date, how='left')
        
    df_master = df_master.fillna(0) # fill missing volumes/values gracefully with 0
    
    # Compute overall shift based strictly on oldest requested date versus newest requested date
    newest_str = valid_fidel_dates[0].strftime('%Y-%m-%d')
    oldest_str = valid_fidel_dates[-1].strftime('%Y-%m-%d')
    df_master['Value Change'] = df_master[f"Val {newest_str}"] - df_master[f"Val {oldest_str}"]

    symbols = list(df_master.index)
    fields = ['sectorname', 'primaryname', 'symbol']
    df_sector_ind = apis.df_symbol_profile(symbols, fields)
    df_sector_ind.dropna(inplace=True)
    df_sector_ind.rename(columns={'symbol': 'Symbol', 'sectorname': 'Sector', 'primaryname': 'Industry'}, inplace=True)

    df_master.index.name = 'Symbol'
    df_master = df_master.reset_index()
    
    df_master = df_sector_ind.merge(df_master, on='Symbol', how='inner')
    return df_master.sort_values(by=['Sector', 'Symbol']), valid_fidel_dates


# --- LAYOUT ---

end_default = datetime.today()
start_default = end_default - timedelta(days=28) # Default to looking back 4 weeks for multiple imports

layout = html.Div([
    html.H3("Portfolio Quantity & Dynamic Value Timelines",
            style={'textAlign': 'center', 'fontFamily': 'sans-serif', 'paddingTop': '20px', 'fontSize': '18px'}),

    html.Div([
        html.Div([
            daq.ToggleSwitch(
                id='view-toggle-changes',
                label=['Overall Negative Change', 'Overall Positive Change'],
                labelPosition='bottom',
                value=True,
                color='#2c3e50'
            ),
        ], style={'display': 'inline-block', 'verticalAlign': 'middle', 'marginRight': '50px'}),

        html.Div([
            dcc.DatePickerRange(
                id='date-picker-range-changes',
                start_date=start_default.date(),
                end_date=end_default.date(),
                display_format='YYYY-MM-DD',
                style={'display': 'inline-block', 'verticalAlign': 'middle'}
            )
        ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
    ], style={'padding': '20px', 'textAlign': 'center'}),

    dcc.Store(id='data-store-changes'),
    dcc.Store(id='fidel-dates-store-changes'),

    html.Div([
        dash_table.DataTable(
            id='changes-table',
            columns=[], # We render this dynamically based on date logic
            sort_action="native",
            export_format="csv",
            style_table={'overflowX': 'auto', 'width': '95%', 'margin': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '12px', 'fontFamily': 'sans-serif'},
            style_header={'backgroundColor': '#f4f4f4', 'fontWeight': 'bold'}
        )
    ], style={'padding': '40px'})
])


# --- CALLBACKS ---

@callback(
    [Output('data-store-changes', 'data'),
     Output('fidel-dates-store-changes', 'data')],
    [Input('date-picker-range-changes', 'start_date'),
     Input('date-picker-range-changes', 'end_date')]
)
def update_data(start_date, end_date):
    df, valid_dates = load_portfolio_data(start_date, end_date)
    
    if df.empty:
        return [], []
        
    # Serialize fidelity dates array safely to strings
    date_strings = [d.strftime('%Y-%m-%d') for d in valid_dates]
    
    return df.to_dict('records'), date_strings

@callback(
    [Output('changes-table', 'data'),
     Output('changes-table', 'columns')],
    [Input('view-toggle-changes', 'value'),
     Input('data-store-changes', 'data'),
     Input('fidel-dates-store-changes', 'data')]
)
def update_table(is_positive, data, date_strings):
    if not data or not date_strings:
        return [], []
    
    df_master = pd.DataFrame(data)
    
    if is_positive:
        df_filtered = df_master[df_master['Value Change'] >= 0].copy()
    else:
        df_filtered = df_master[df_master['Value Change'] < 0].copy()
    
    # Pre-render format rules
    df_filtered['Value Change'] = df_filtered['Value Change'].round(2)
    
    # Establish base columns
    columns = [
        {"name": "Symbol", "id": "Symbol"},
        {"name": "Sector", "id": "Sector"},
        {"name": "Industry", "id": "Industry"},
        {
            "name": "Overall Value Change",
            "id": "Value Change",
            "type": "numeric",
            "format": Format(precision=2, scheme=Scheme.fixed)
        }
    ]
    
    # Add pairs sequentially per distinct fidelity date
    for dt_str in date_strings:
        df_filtered[f"Qty {dt_str}"] = df_filtered[f"Qty {dt_str}"].round(0)
        df_filtered[f"Val {dt_str}"] = df_filtered[f"Val {dt_str}"].round(2)
        
        columns.extend([
            {
                "name": f"Qty {dt_str}",
                "id": f"Qty {dt_str}",
                "type": "numeric",
                "format": Format(precision=0, scheme=Scheme.fixed)
            },
            {
                "name": f"Val {dt_str}",
                "id": f"Val {dt_str}",
                "type": "numeric",
                "format": Format(precision=2, scheme=Scheme.fixed)
            }
        ])
    
    return df_filtered.to_dict('records'), columns
