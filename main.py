from geo_utils.io import load_gdf
from geo_utils.merge import spatial_join_elevation

import pandas as pd
import json

import config

def prepare_data(dataset, elevation_layer):
    # Select elevation GeoJSON based on dropdown
    if elevation_layer == 'elevation1':
        gdf_elev = load_gdf(config.Elevation_geojson_path_1)
    elif elevation_layer == 'elevation2':
        gdf_elev = load_gdf(config.Elevation_geojson_path_2)
    else:
        return None, None, None

    # Select base shapefile and label column
    if dataset == 'ripGeo':
        gdf_shp = load_gdf(config.Ripeo_path)
        label_col = 'DEN_RIP'
    elif dataset == 'Reg':
        gdf_shp = load_gdf(config.Reg_path)
        label_col = 'DEN_REG'
    elif dataset == 'Prov':
        gdf_shp = load_gdf(config.Prov_path)
        label_col = 'DEN_PROV'
    else:
        return None, None, None

    gdf_joined = spatial_join_elevation(gdf_shp, gdf_elev, elevation_col='elevation_band')
    gdf_joined["elevation_band"] = pd.to_numeric(gdf_joined["elevation_band"], errors='coerce')
    gdf_joined = gdf_joined.drop_duplicates(subset="geometry")
    gdf_joined = gdf_joined.dropna(subset=['elevation_band'])
    gdf_joined = gdf_joined.reset_index(drop=True)
    gdf_joined["id"] = gdf_joined.index.astype(str)

    return gdf_joined, label_col, json.loads(gdf_joined.to_json())