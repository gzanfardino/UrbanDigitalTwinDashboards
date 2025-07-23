from visualization.Webgisplot import webgis_plot

from dash import Dash, dcc, html, Input, Output, register_page, callback
import dash_leaflet as dl
#import dash_html_components as html
import requests

# === Dash Register Setup ===

register_page(__name__, name = "WebGis Viewer", path='/Webgis')



# WebGis Tab
layout = html.Div([
            html.Br(),
            # Add WebGIS content here
            html.Label("WebGIS Map Visualization"),
            html.Br(),
            # Add Loading spinner for WebGIS map
            dcc.Loading(
                id="loading-webgis",
                type="circle",
                children=[
                    # WebGIS map using iframe
                    html.Iframe(
                        id="webgis-iframe",  # Make it accessible for updates
                        src="http://webgis.comuneaq.usra.it/mappa_def.php",  # Default URL
                        width="100%",  # Takes full width
                        height="600px",  # Set the height for the iframe
                        style={'border': 'none'}
                    )
                ]
            )
        ])


# App Callbacks

# Callback for WebGis
@callback(
    Output('webgis-iframe', 'src'),
    [
        Input('dataset-dropdown', 'value'),
        #Input('elevation-dropdown', 'value')
    ]
)
def update_webgis(dataset, elevation_layer, elevation_range):
    return webgis_plot(dataset, elevation_layer, elevation_range)

