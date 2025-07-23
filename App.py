from dash import Dash, dcc, html, page_registry, page_container
import dash_bootstrap_components as dbc
import dash_leaflet as dl

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    dbc.themes.SLATE
]

# === Dash App Setup ===
app = Dash(__name__, external_stylesheets=external_stylesheets, use_pages= True, suppress_callback_exceptions=True)

# Define Navigation Bar
navbar = dbc.NavbarSimple(
    children = [
        dbc.NavItem(dbc.NavLink('Elevation Viewer', href = '/')),
        dbc.NavItem(dbc.NavLink('Informed GeoJson', href = '/Informed')),
        dbc.NavItem(dbc.NavLink('Risk Zones', href = '/RiskZone')),
        dbc.NavItem(dbc.NavLink('Istat Data', href = '/IstatData')),
        dbc.NavItem(dbc.NavLink('WebGis Viewer', href = '/Webgis')),
        dbc.NavItem(dbc.NavLink('Aristocrazia', href = '/Aristocrazia')),
    ],
    brand="Dashboard",
    brand_href='/',
    color='dark',
    dark = True
)

# Define layout
app.layout = html.Div([
    dcc.Store(id='shared-map-focus', storage_type='session') , # Added 29th
    navbar,
    page_container
])

if __name__ == '__main__':
    app.run(debug=True)