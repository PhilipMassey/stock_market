import dash
import dash_labs as dl
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__, plugins=[dl.plugins.pages], external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# for x in dash.page_registry.values():
#     print(x)

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
    [navbar, dl.plugins.page_container],
    fluid=True,
)

@app.server.route("/health")
def health():
  return "OK",200


if __name__ == "__main__":
    app.run_server(debug=True)
