import dash
from dash import dcc, html, Input, Output, callback

dash.register_page(__name__, path="/")

layout = html.Div([
        html.H1('Home Page')
])