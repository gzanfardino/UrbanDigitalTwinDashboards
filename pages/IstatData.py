import geopandas as gpd
from dash import register_page, html, dcc, callback, Input, Output, ALL, MATCH, callback_context, State, ClientsideFunction
import dash_leaflet as dl
from dash.exceptions import PreventUpdate
from geo_utils.risk_analysis import province_name_mapping, color_map, istat_risk_map
import os
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import ctx  # to check which Input triggered the callback
from dash.dependencies import Input, Output
from dash_extensions.enrich import DashProxy
from dash_extensions.javascript import assign

from shapely.geometry import mapping
import json
import config
from collections import defaultdict

register_page(__name__, name="Istat Data", path="/IstatData")




def flip_geojson_coordinates(filepath):
    with open(filepath, "r") as f:
        geojson_data = json.load(f)

    for feature in geojson_data["features"]:
        geom_type = feature["geometry"]["type"]
        coords = feature["geometry"]["coordinates"]

        def flip_coords(coord_list):
            return [coord[::-1] for coord in coord_list]

        if geom_type == "Polygon":
            feature["geometry"]["coordinates"] = [flip_coords(ring) for ring in coords]
        elif geom_type == "MultiPolygon":
            feature["geometry"]["coordinates"] = [
                [flip_coords(ring) for ring in polygon] for polygon in coords
            ]

    temp_path = filepath + ".tmp"
    with open(temp_path, "w") as f:
        json.dump(geojson_data, f)
    os.replace(temp_path, filepath)


# Load shapefiles
regions_gdf = gpd.read_file(config.Reg_path)
provinces_gdf = gpd.read_file(config.Prov_path).to_crs("EPSG:4326")  # Ensure CRS matches building data

geojson_path = 'all_building.geojson'
flip_geojson_coordinates(geojson_path)
init_gdf = gpd.read_file(geojson_path).to_crs("EPSG:4326")


def normalize_province_name(raw_name):
    if not raw_name:
        return raw_name
    key = raw_name.strip().upper()
    return province_name_mapping.get(key, raw_name)

# Get bounding box for a given province
def get_province_bbox(province):
    normalized = normalize_province_name(province)
    df = provinces_gdf[provinces_gdf["DEN_PROV"] == normalized]
    if df.empty:
        return None
    return tuple(df.total_bounds)

def filter_buildings_by_province(buildings_gdf, province_name):
    normalized = normalize_province_name(province_name)
    filtered = buildings_gdf[
        buildings_gdf["provincia"].str.upper().str.strip() == normalized.upper()
    ]
    return filtered

def get_normalized_provinces_for_region(region_code):
    raw_provs = region_province_map.get(region_code, [])
    normalized_provs = sorted(set(normalize_province_name(p) for p in raw_provs))
    return normalized_provs

# Mapping between regions and provinces
region_province_map = {
    region: list(provinces_gdf[provinces_gdf["COD_REG"] == region]["DEN_PROV"].unique())
    for region in provinces_gdf["COD_REG"].unique()
}

# Dropdown data setup
region_code_name_map = dict(zip(regions_gdf["COD_REG"], regions_gdf["DEN_REG"]))
region_name_code_map = {v: k for k, v in region_code_name_map.items()}

region_options = [{"label": name, "value": name} for name in region_name_code_map]
province_options = [{"label": normalize_province_name(p), "value": normalize_province_name(p)} for p in region_province_map.get(9, [])]

# Map raw ISTAT risk to descriptive labels
init_gdf["risk_level"] = init_gdf["tipologia"].astype(str).map(istat_risk_map)


risk_options = [
    {"label": "Low Risk", "value": "Low"},
    {"label": "Medium Risk", "value": "Medium"},
    {"label": "High Risk", "value": "High"},
]

# Legend
def get_istat_legend():
    return [
        html.Div([
            html.H4("Risk Zones"),
            html.Div([
                html.Span([
                    html.Span(style={
                        "display": "inline-block",
                        "width": "12px",
                        "height": "8px",
                        "backgroundColor": color_map[risk],
                        "marginRight": "5px",
                        "border": "1px solid #333"
                    }),
                    risk
                ], style={"marginRight": "15px"})  # spacing between items
                for risk in color_map
            ], style={"display": "flex", "flexDirection": "row", "alignItems": "center"})
        ], style={
            "position": "absolute",
            "top": "50px",
            "right": "10px",
            "backgroundColor": "white",
            "padding": "10px",
            "zIndex": "1000",
            "border": "1px solid #ccc",
            "borderRadius": "5px",
            "display": "inline-block"
        })
    ]

layout = html.Div([
    dcc.Store(id="shared-geodata-selection"),
    dcc.Store(id="building-color-store", data={}),
    dcc.Store(id="modified-risk-store", data={}, storage_type="local"),
    dcc.Store(id="clicked-building-id"),

    html.Div([
        dcc.Dropdown(id="istat-Region-dropdown", options=region_options, value="Toscana",
                     placeholder="Select Region", style={"width": "48%", "marginRight": "1%"}),
        dcc.Dropdown(id="istat-provinces-dropdown", options=province_options,
                     value="Prato", placeholder="Select Province", style={"width": "48%"}),
        dcc.Dropdown(id="istat-building-dropdown",
                     placeholder="Select a building ID", style={"width": "48%", "marginRight": "2%"})
    ], style={"display": "flex", "margin": "10px"}),

    html.Div([
        # LEFT: Map
        dl.Map(id="istat-map", center=[43.77, 11.25], zoom=15,
               children=[
                   dl.TileLayer(),
                   dl.LayerGroup(id="istat-layers"),
                   dl.Marker(id="istat-building-marker", position=[41.9, 12.5]),
                   dl.ScaleControl(position="bottomleft")
               ],
               style={"width": "65%", "height": "90vh", "position": "relative"}),

        # RIGHT: Interactive graph
        html.Div([
            dcc.Loading(
                id="loading-istat-height",
                type="circle",
                children=[
                    dcc.Graph(id="istat-height-graph", style={"height": "40vh", "width": "100%"})
                ]
            ),
            #dcc.Graph(id="istat-height-graph", style={"height": "40vh", "width": "100%"}),
            dcc.Loading(
                id="loading-istat-line",
                type="circle",
                children=[
                    dcc.Graph(id="istat-line-graph", style={"height": "50vh", "width": "100%"})
                ]
            ),
            #dcc.Graph(id="istat-line-graph", style={"height": "50vh", "width": "100%"}),
        ], style={"width": "35%", "paddingLeft": "10px", "boxSizing": "border-box"}),
    ], style={"display": "flex", "flexDirection": "row"}),

    # Legend overlay
    *get_istat_legend(),
])

initial_risk_lookup = dict(zip(init_gdf["id_edifici"].astype(str), init_gdf["risk_level"]))


on_each_feature = assign("""
function(feature, layer, context){
    const id = feature.properties.id_edifici;
    const risk = feature.properties.risk_level;

    const popupContent = `
        <div>
            <h4 style="margin:0;">Building ID: ${id}</h4>
            <p style="margin:0;">Risk Level: ${risk}</p>
            <br>
            <select id="dropdown-${id}">
                <option value="Low" ${risk === "Low" ? "selected" : ""}>Low Risk</option>
                <option value="Medium" ${risk === "Medium" ? "selected" : ""}>Medium Risk</option>
                <option value="High" ${risk === "High" ? "selected" : ""}>High Risk</option>
            </select>
        </div>
    `;

    layer.bindPopup(popupContent, {sticky: true, direction: "top", className: "custom-tooltip"});
}
""")



@callback(
    Output("istat-provinces-dropdown", "options"),
    Output("istat-provinces-dropdown", "value"),
    Input("istat-Region-dropdown", "value"),
)
def update_provinces(region_name):
    if not region_name:
        raise PreventUpdate

    region_code = region_name_code_map.get(region_name)
    provinces = get_normalized_provinces_for_region(region_code)
    province_options = [{"label": p, "value": p} for p in provinces]

    default_prov = province_options[0]["value"] if province_options else None
    return province_options, default_prov


@callback(
    Output("istat-building-dropdown", "options"),
    Output("istat-map", "center"),
    Output("istat-layers", "children"),  # Outputting the list of GeoJSON layers here
    Input("istat-provinces-dropdown", "value"),
    prevent_initial_call=True
)
def update_buildings_dropdown(province):
    if not province:
        raise PreventUpdate

    bbox = get_province_bbox(province)
    buildings_gdf = filter_buildings_by_province(init_gdf, province)

    # Ensure risk_level column is present and mapped
    if "risk_level" not in buildings_gdf.columns:
        buildings_gdf["risk_level"] = buildings_gdf["tipologia"].astype(str).map(istat_risk_map)
        print("Unique risk levels:", buildings_gdf["risk_level"].unique())

    # Prepare building dropdown options
    building_options = []
    if "id_edifici" in buildings_gdf.columns:
        building_options = [{"label": str(bid), "value": str(bid)} for bid in buildings_gdf["id_edifici"].unique()]

    # Map center calculation
    center = [(bbox[1] + bbox[3]) / 2, (bbox[0] + bbox[2]) / 2] if bbox else [41.9, 12.5]

    # Group features by risk_level
    grouped_features = defaultdict(list)
    for _, row in buildings_gdf.iterrows():
        if not row.geometry.is_empty:
            feature = {
                "type": "Feature",
                "geometry": mapping(row.geometry),
                "properties": {
                    "id_edifici": str(row.get("id_edifici", "")),
                    "risk_level": row.get("risk_level", "Low")
                }
            }
            grouped_features[row.get("risk_level", "Low")].append(feature)
    

    # Build a GeoJSON layer per risk group
    geojson_layers = []
    for risk, features in grouped_features.items():
        geojson_layers.append(
            dl.GeoJSON(
                data={"type": "FeatureCollection", "features": features},
                id={"type": "geojson-layer", "risk": risk},
                #id=f"istat-building-layer-{risk.lower()}",
                options=dict(style=dict(
                    color=color_map.get(risk, "#999"),
                    weight=1,
                    fillOpacity=0.5
                )),
                onEachFeature=on_each_feature,
                hoverStyle={"weight": 3, "color": "#333", "fillOpacity": 0.7},
                zoomToBoundsOnClick=False,
                eventHandlers={"click": True},
            )
        )

    return building_options, center, geojson_layers


@callback(
    Output("istat-building-marker", "position", allow_duplicate=True),
    Output("istat-map", "center", allow_duplicate=True),
    Input("istat-building-dropdown", "value"),
    Input("istat-provinces-dropdown", "value"),
    Input("istat-map", "click_lat_lng"), 
    prevent_initial_call=True
)
def update_marker_position_and_center(building_id, province, click_lat_lng):
    # Determine which input triggered the callback
    triggered_id = ctx.triggered_id

    if triggered_id == "istat-map" and click_lat_lng:
        # User clicked on the map - center on that location
        return click_lat_lng, click_lat_lng

    # Fallback to dropdown-based behavior
    if not building_id or not province:
        raise PreventUpdate

    buildings_gdf = filter_buildings_by_province(init_gdf, province)
    row = buildings_gdf[buildings_gdf["id_edifici"].astype(str) == str(building_id)]
    if row.empty:
        raise PreventUpdate

    geom = row.iloc[0].geometry
    if geom.is_empty:
        raise PreventUpdate

    coords = [geom.centroid.y, geom.centroid.x] if geom.geom_type != "Point" else [geom.y, geom.x]
    return coords, coords



@callback(
    Output("istat-layers", "children", allow_duplicate=True),
    Input("modified-risk-store", "data"),
    Input("istat-provinces-dropdown", "value"),
    prevent_initial_call=True,
)
def update_building_colors(selected_risks, province):
    if not province:
        raise PreventUpdate

    buildings_gdf = filter_buildings_by_province(init_gdf, province)

    # Group features by updated risk level
    grouped_features = defaultdict(list)
    for _, row in buildings_gdf.iterrows():
        bid = row.get("id_edifici", "")
        risk = selected_risks.get(bid, row.get("risk_level", "Low"))
        feature = {
            "type": "Feature",
            "geometry": mapping(row.geometry),
            "properties": {
                "id_edifici": str(row.get("id_edifici", "")),
                "risk_level": risk
            }
        }
        grouped_features[risk].append(feature)

    geojson_layers = []
    for risk, features in grouped_features.items():
        geojson_layers.append(
            dl.GeoJSON(
                data={"type": "FeatureCollection", "features": features},
                #id=f"istat-building-layer-{risk.lower()}",
                id={"type": "geojson-layer", "risk": risk},
                options=dict(style=dict(
                    color=color_map.get(risk, "#999"),
                    weight=1,
                    fillOpacity=0.5
                )),
                hoverStyle={"weight": 3, "color": "#333", "fillOpacity": 0.7},
                zoomToBoundsOnClick=False,
                onEachFeature=on_each_feature,
                eventHandlers={"click": True},
            )
        )

    return geojson_layers

@callback(
    Output("modified-risk-store", "data"),
    Input({"type": "risk-dropdown", "index": ALL}, "value"),
    State({"type": "risk-dropdown", "index": ALL}, "id"),
    prevent_initial_call=True
)
def store_selected_risks(selected_values, ids):
    if not selected_values or not ids:
        raise PreventUpdate
    return {id_["index"].split("_")[0]: value for id_, value in zip(ids, selected_values)}



@callback(
    Output("istat-line-graph", "figure"),
    Input("modified-risk-store", "data"),
    Input("istat-provinces-dropdown", "value"),
    prevent_initial_call=True
)
def update_line_graph(risk_data, province):
    if not province:
        raise PreventUpdate

    buildings_gdf = filter_buildings_by_province(init_gdf, province).copy()

    # Update risk levels using modified risk data
    buildings_gdf["risk_level"] = buildings_gdf["id_edifici"].astype(str).map(
        lambda bid: risk_data.get(str(bid), initial_risk_lookup.get(str(bid), "Low"))
    )

    # Ensure area_ exists and is numeric
    if "area_" not in buildings_gdf.columns:
        raise PreventUpdate

    area_bins = [0, 50, 100, 200, 500, 1000, float("inf")]
    area_labels = ["0-50", "50-100", "100-200", "200-500", "500-1000", "1000+"]

    # Convert and clean
    buildings_gdf["area_"] = pd.to_numeric(buildings_gdf["area_"], errors="coerce")
    buildings_gdf = buildings_gdf.dropna(subset=["area_"])

    # Apply binning
    buildings_gdf["area_bin"] = pd.cut(buildings_gdf["area_"], bins=area_bins, labels=area_labels)


    # Group by area_bin and risk_level
    grouped = buildings_gdf.groupby(["area_bin", "risk_level"], observed=True).size().reset_index(name="count")

    # Ensure consistent bin order
    grouped["area_bin"] = pd.Categorical(grouped["area_bin"], categories=area_labels, ordered=True)
    grouped = grouped.sort_values("area_bin")

    color_map_for_line = {
    "Low": "green",
    "Medium": "orange",
    "High": "red"
    }


    fig = px.line(
        grouped,
        x="area_bin",
        y="count",
        color="risk_level",
        markers=True,  # optional: to show markers at data points
        color_discrete_map=color_map_for_line,
        labels={"area_bin": "Building Area Range (m²)", "count": "Number of Buildings"},
        title="Risk Distribution by Building Area",
        category_orders={"risk_level": ["High", "Medium", "Low"]}
    )
    return fig



@callback(
    Output("istat-height-graph", "figure"),
    Input("istat-building-dropdown", "value"),
    Input({"type": "geojson-layer", "risk": ALL}, "clickData"),
    Input("istat-provinces-dropdown", "value"),
    prevent_initial_call=True
)
def update_height_graph(building_id, click_datas, province):
    building_ids = set()
    building_risks = {}

    # Collect building IDs and their risks
    for click_data in click_datas:
        if click_data:
            props = click_data.get("properties", {})
            bid = str(props.get("id_edifici"))
            risk = props.get("risk_level", "Unknown")
            if bid:
                building_ids.add(bid)
                building_risks[bid] = risk

    if building_id:
        building_ids.add(str(building_id))
        if str(building_id) not in building_risks:
            building_risks[str(building_id)] = "Unknown"

    if not building_ids or not province:
        raise PreventUpdate

    buildings_gdf = filter_buildings_by_province(init_gdf, province)
    matched_buildings = buildings_gdf[buildings_gdf["id_edifici"].astype(str).isin(building_ids)]

    if matched_buildings.empty:
        raise PreventUpdate

    # Prepare height data and add risk info
    all_height_data = []
    for _, building in matched_buildings.iterrows():
        bid = str(building["id_edifici"])
        risk = building_risks.get(bid, "Unknown")
        for metric, value in {
            "Ground Level": building["quota_suolo"],
            "Eaves Height": building["quota_gronda"],
            "Total Height": building["altezza"]
        }.items():
            all_height_data.append({
                "Building ID": bid,
                "Metric": metric,
                "Value (m)": value,
                "Risk Level": risk
            })

    height_df = pd.DataFrame(all_height_data)

    # Map risk levels to colors
    risk_color_map = {
        "Low": "green",
        "Medium": "orange",
        "High": "red"
    }
    height_df["Color"] = height_df["Risk Level"].map(risk_color_map).fillna("gray")

    # Build the bar chart with manual colors, no legend
    fig = px.bar(
        height_df,
        x="Metric",
        y="Value (m)",
        color="Building ID",
        barmode="group",
        text_auto=True,
        title="Height Metrics for Selected Buildings"
    )

    # Apply custom colors to each bar
    fig.for_each_trace(lambda t: t.update(marker_color=[
        row["Color"] for _, row in height_df[height_df["Building ID"] == t.name].iterrows()
    ]))

    # Remove legend
    fig.update_layout(showlegend=False)

    return fig

