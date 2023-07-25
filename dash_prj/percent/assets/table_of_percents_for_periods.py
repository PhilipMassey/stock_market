import dash
from dash import html
from dash import dcc
from dash import dash_table as dt
from dash.dependencies import Output, Input
import market_data as md
import performance as pf


label_period = html.Label('Select Period', style={'font-size':'20px'})
radio_period = html.Div([
    dcc.RadioItems(
        id='radio-ndays_range',
        options=[
            {'label': '5, 10, 21, 64, 128, 252 days', 'value': pf.wfm3612_option},
            {'label': 'Monthly', 'value': pf.monthly_option}
                ],
        labelStyle={'display': 'block'},
        value=pf.monthly_option, ),
])

label_perc_or_mean = html.Label('Select Percentage calculation',style={'font-size':'20px'})
radio_perc_or_mean = html.Div([
    dcc.RadioItems(
        id='radio-perc-or-mean',
        options=[
            {'label': 'Portfolio Mean', 'value': pf.mean_option},
            {'label': 'Symbol percent change', 'value': pf.perc_option}
            ],
       labelStyle={'display': 'block'},
       value=pf.perc_option, ),
])

period_block = html.Div([label_period, radio_period],
                        style={'width':'50%', 'float':'left'})

perc_or_mean_block = html.Div([label_perc_or_mean, radio_perc_or_mean],
                         style = {'margin-left': '50%'})


dirs = md.get_portfolio_dirs()
dropdowns = html.Div([
        html.Div([
            html.Label('Portfolio Directories'),
            dcc.Dropdown(id='dropdown-dirs', options=[{'label': i, 'value': i} for i in dirs], value=None)],
            style={'width': '49%', 'float': 'left'}
            ),
    html.Div([
       html.Label('Portfolios'),
        dcc.Dropdown(id='dropdown-ports', options=[], value=None)],
        style = {'width': '49%','float': 'right'}
    ),

], style= {'width': '100%','display': 'inline-block'})

results_date = html.Div('Current date',id='results-date')
results_table = html.Div(id="results-table")


app = dash.Dash(__name__)
app.layout = html.Div([period_block, perc_or_mean_block, results_date, dropdowns, results_table])


#callback on directory selection
@app.callback(
    Output('dropdown-ports', 'options'),
    [Input('dropdown-dirs', 'value')])
def update_dropdown_ports(value):
    if(value != None):
        df_port_symbols = md.get_dir_port_symbols(value)
        return [{'label': i, 'value': i} for i in sorted(df_port_symbols["portfolio"].unique())]
    else:
        return []


#update table based on
@app.callback(
    Output('results-date','children'),
    Output('results-table', 'children'),
    Input('radio-ndays_range', 'value'),
    Input('radio-perc-or-mean', 'value'),
    Input('dropdown-dirs', 'value'),
    Input('dropdown-ports', 'value')
)
def update_table(period, perc_or_mean, directory, port):
    results_date_value = 'No results'
    import pandas as pd
    df = pd.DataFrame({'options':[period, perc_or_mean], 'portfolios':[directory, port]})
    results_date_value, df = pf.df_wfm3612_option(period, directory, port)
    if period == pf.monthly_option:
        #print(ndays_range, perc_or_mean, directory, port)
        results_date_value,df = pf.df_monthly_option(perc_or_mean, directory, port)
        #print(results_date_value,df.head(2))
    elif period == pf.wfm3612_option:
        results_date_value, df = pf.df_wfm3612_option(perc_or_mean, directory, port)
    return (results_date_value,
            dt.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            style_cell={
                'font_family': 'arial',
                'font_size': '20px',
                'text_align': 'center'
            },
            sort_action='native'))

if __name__ == "__main__":
    app.run_server(debug=True)


