from dash import Dash, html, dcc
import dash

app = Dash(__name__, use_pages=True, pages_folder="")

dash.register_page("home", path='/', layout=html.Div('Home Page'))
dash.register_page("analytics", layout=html.Div('Analytics'))

app.layout = html.Div([
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container,
])

if __name__ == '__main__':
    app.run(debug=True)
