from dash import html
import dash

layout = html.H1("Custom 404")

dash.register_page(__name__, path="/404")
