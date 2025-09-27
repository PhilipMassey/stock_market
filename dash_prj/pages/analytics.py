import dash
from dash import dcc, html, Input, Output, callback

dash.register_page(__name__, path="/historical-analysis")

layout = html.Div([
    html.H1('Historical Analysis Page')
])
