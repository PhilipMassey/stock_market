# https://community.plotly.com/t/introducing-dash-pages-a-dash-2-x-feature-preview/57775?page=7
import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
from flask import Flask, jsonify

app = dash.Dash(
    __name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP]
)

for x in dash.page_registry.values():
    print(x)

navbar = dbc.NavbarSimple(
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(page["name"], href=page["path"])
            for page in dash.page_registry.values()
            if page["module"] != "pages.not_found_404"
        ],
        nav=True,
        label="More Pages",
    ),
    brand="",
    color="primary",
    dark=True,
    className="mb-2",
)

app.layout = dbc.Container(
    [navbar, dash.page_container],
    fluid=True,
)


@app.server.route("/health")
def health():
    state = {"status": "UP"}
    return jsonify(state)


if __name__ == "__main__":
    app.run(debug=True, port=8561)
