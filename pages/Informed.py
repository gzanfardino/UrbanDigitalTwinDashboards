from visualization.Informedplot import InformedGeoPlotter
from main import prepare_data # Added 29th


from dash import Dash, dcc, html, Input, Output, register_page, callback
import dash_leaflet as dl
#import dash_html_components as html
import requests


# === Dash Register Setup ===

register_page(__name__, name = "Informed GeoJson", path='/Informed')

# Instantiate plotter
plotter = InformedGeoPlotter()


layout = html.Div([
    html.Br(),
    dcc.Store(id='shared-map-focus', storage_type='session'),
    html.Label("Select Geographic Dataset"),
    dcc.Dropdown(
        id='dataset-dropdown',
        options=[
            {'label': 'Ripartizione Geografica', 'value': 'ripGeo'},
            {'label': 'Regione', 'value': 'Reg'},
            {'label': 'Provincia', 'value': 'Prov'}
        ],
        value='ripGeo'
    ),
    # Dropdown for Elevation
    html.Label("Select Elevation"),
    dcc.Dropdown(
        id='elevation-dropdown',
        options=[
            {'label': 'Elevation 1', 'value': 'elevation1'},
            {'label': 'Elevation 2', 'value': 'elevation2'}
        ],
        value='elevation1'
    ),
    # Add Slider
    html.Label("Select Elevation Range"),
    dcc.RangeSlider(
        id='elevation-range-slider',
        min=0,
        max=25,
        step=1,
        marks={i: str(i) for i in range(0, 25, 5)},
        value=[0, 25]
    ),
    html.Br(),
    # Add progress bar
    dcc.Loading(
        id="loading-choropleth",
        type="circle",
        children=[
            dcc.Graph(id='choropleth-map')
        ]
    )
])


# Callback for Informed GeoJson Dataset
@callback(
    Output('choropleth-map', 'figure'),
    Input('dataset-dropdown', 'value'),
    Input('elevation-dropdown', 'value'),
    Input('elevation-range-slider', 'value')
)
def update_map(dataset, elevation_layer, elevation_range):
    return plotter.informed_geojson(dataset, elevation_layer, elevation_range)