from visualization.Elevationplot import ElevationPlotter

from dash import Dash, dcc, html, Input, Output, register_page, callback
import dash_leaflet as dl
#import dash_html_components as html
import requests



# === Dash Register Setup ===

register_page(__name__, name = "Elevation Viewer", path='/')

# Create an instance
plotter = ElevationPlotter()


layout = html.Div([
            html.Br(),
            # Dropdown for Elevation
            html.Label("Select Elevation"),
            dcc.Dropdown(
                id='raw-elevation-dropdown',
                options=[
                    {'label': 'Elevation 1', 'value': 'elevation1'},
                    {'label': 'Elevation 2', 'value': 'elevation2'}
                ],
                    value='elevation1'
            ),
            html.Br(),
            # Add progress bar
            dcc.Loading(
                id="loading-raw-elevation",
                type="circle",
                children=[
                    dcc.Graph(id='raw-elevation-map')
                ]
            )
        ])




# App Callbacks

# Callback for Elevation Data
@callback(
    Output('raw-elevation-map', 'figure'),
    Input('raw-elevation-dropdown', 'value')
)
def update_raw_elevation_map(elevation_layer):
    return plotter.independent_tif(elevation_layer)