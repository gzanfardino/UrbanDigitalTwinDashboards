from dash import register_page
import dash_leaflet as dl
from visualization.RiskZonePlot import RiskZonePlot
from geo_utils.risk_analysis import color_map
from main import prepare_data 
from geo_utils.io import load_gdf
from geo_utils.region_province_map import region_province_map, province_bboxes
import config
from dash import html, dcc, callback, Input, Output, State, ctx
from dash.exceptions import PreventUpdate

register_page(__name__, name="Risk Zoning", path="/RiskZone")

# Instantiate the class
risk_plot = RiskZonePlot()



region_options = [{"label": region, "value": region} for region in region_province_map]
province_options = [{"label": name, "value": name} for name in province_bboxes]

layout = html.Div([
    dcc.Store(id='shared-geodata-selection'),
    html.Div([
        dcc.Dropdown(
            id='Region-dropdown',
            options=region_options,
            value='Lombardy',
            placeholder="Select Region",
            style={"width": "48%", "marginRight": "1%"}
        ),
        dcc.Dropdown(
            id='provinces-dropdown',
            options=province_options,
            value='Milan',
            placeholder="Select Provincia",
            style={"width": "48%", "marginRight": "1%"}
        ),
        dcc.Dropdown(
            id="building-dropdown",
            options=risk_plot.get_building_options(),
            placeholder="Select a building ID",
            style={"width": "48%", "marginRight": "2%"}
        )
    ], style={"display": "flex", "marginBottom": "10px", "marginTop": "10px"}),

    dl.Map(
        id="map",
        center=risk_plot.default_position,
        zoom=risk_plot.default_zoom,
        children=[
            dl.TileLayer(),
            *risk_plot.get_layers(),
            dl.Marker(id="building-marker", position=risk_plot.default_position),
            dl.ScaleControl(position="bottomleft")
        ],
        style={'width': '100%', 'height': '90vh', 'position': 'relative'}
    ),

    dcc.Loading(
        id="loading-choropleth",
        type="circle",  # or 'default', 'dot'
        fullscreen=False,
        children=[
            dcc.Graph(id='choropleth-map', style={"height": "80vh"})
        ],
        style={"marginTop": "20px"}
    ),

    *risk_plot.get_legend(),
])


@callback(
    Output("building-marker", "position", allow_duplicate=True),
    Output("building-marker", "children", allow_duplicate=True),
    Output("map", "center", allow_duplicate=True),
    Output("map", "zoom", allow_duplicate=True),
    Input("building-dropdown", "value"),
    prevent_initial_call=True
)
def update_marker_from_dropdown(building_id):
    return risk_plot.get_dropdown_info(building_id)


@callback(
    Output("building-marker", "position", allow_duplicate=True),
    Output("building-marker", "children", allow_duplicate=True),
    [Input(f"geojson-{risk}", "clickData") for risk in color_map],
    prevent_initial_call=True
)
def on_any_geojson_click(*click_datas):
    return risk_plot.get_click_info(*click_datas)



@callback(
    Output("provinces-dropdown", "options", allow_duplicate=True),
    Output("provinces-dropdown", "value", allow_duplicate=True),
    Input("Region-dropdown", "value"),
    prevent_initial_call=True
)
def update_provinces(region_name):
    if not region_name or region_name not in region_province_map:
        raise PreventUpdate
    provinces = region_province_map[region_name]
    options = [{"label": p, "value": p} for p in provinces]
    return options, provinces[0]  # Auto-select first province





@callback(
    Output("map", "children", allow_duplicate=True),
    Output("map", "center", allow_duplicate=True),
    Output("map", "zoom", allow_duplicate=True),
    Output("building-dropdown", "options", allow_duplicate=True),
    Input("provinces-dropdown", "value"),
    prevent_initial_call=True
)
def update_province_map(province_name):
    if province_name not in province_bboxes:
        raise PreventUpdate

    new_plot = RiskZonePlot(bbox=province_bboxes[province_name])

    # Store the new object in memory for callbacks
    global risk_plot
    risk_plot = new_plot

    children = [
        dl.TileLayer(),
        *new_plot.get_layers(),
        dl.Marker(id="building-marker", position=new_plot.default_position),
        dl.ScaleControl(position="bottomleft")
    ]

    return children, new_plot.default_position, new_plot.default_zoom, new_plot.get_building_options()

