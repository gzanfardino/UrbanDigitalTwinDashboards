from geo_utils.io import load_gdf
from main import prepare_data
import config

import json
import pandas as pd
import plotly.express as px


class InformedGeoPlotter:
    def __init__(self):
        self.color_schemes = {
            "elevation1": "Viridis",
            "elevation2": "Cividis"
        }

    def informed_geojson(self, dataset, elevation_layer, elevation_range):
        gdf, label_col, geojson_data = prepare_data(dataset, elevation_layer)

        if gdf is None:
            return px.scatter_mapbox()

        min_elev, max_elev = elevation_range
        gdf = gdf[
            (gdf["elevation_band"] >= min_elev) &
            (gdf["elevation_band"] <= max_elev)
        ]

        gdf["hover_text"] = (
            "Region: " + gdf[label_col].astype(str) +
            "<br>Elevation: " + gdf["elevation_band"].astype(str)
        )

        color_scale = self.color_schemes.get(elevation_layer, "Viridis")

        gdf_proj = gdf.to_crs(epsg=3857)
        center_lat = gdf_proj.geometry.centroid.to_crs(4326).y.mean()
        center_lon = gdf_proj.geometry.centroid.to_crs(4326).x.mean()

        fig = px.choropleth_map(
            gdf,
            geojson=geojson_data,
            locations='id',
            color='elevation_band',
            hover_name=label_col,
            hover_data={"id": False, "elevation_band": True},
            color_continuous_scale=color_scale,
            center={"lat": center_lat, "lon": center_lon},
            zoom=4,
            opacity=0.6
        )

        fig.update_layout(
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            title=f"{dataset} with {elevation_layer} (Elevation {min_elev}–{max_elev})"
        )

        return fig
