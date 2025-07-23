from geo_utils.io import load_gdf
from geo_utils.merge import spatial_join_elevation
from main import prepare_data
import config

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# WebGis Plot
def webgis_plot(dataset, elevation_layer, elevation_range):
    # Capture selected area and elevation range, adjust the WebGIS URL accordingly
    region = "default_region"  # Set default region, this will depend on your actual data
    zoom = 10  # Adjust the zoom level dynamically based on elevation or other parameters

    # Based on the dropdown selection, determine the region or area for the WebGIS map
    if dataset == "ripGeo":
        region = "region_1"
    elif dataset == "Reg":
        region = "region_2"
    elif dataset == "Prov":
        region = "region_3"

    # You can adjust zoom level or other parameters based on elevation or range
    min_elev, max_elev = elevation_range
    if max_elev > 20:
        zoom = 12
    else:
        zoom = 10

    # Construct the WebGIS URL with dynamic parameters
    webgis_url = f"http://webgis.comuneaq.usra.it/mappa_def.php?region={region}&zoom={zoom}"

    return webgis_url