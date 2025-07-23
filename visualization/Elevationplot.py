from geo_utils.io import load_gdf
import config

import json
import pandas as pd
import plotly.express as px


class ElevationPlotter:
    def __init__(self):
        self.elevation_sources = {
            "elevation1": config.Elevation_geojson_path_1,
            "elevation2": config.Elevation_geojson_path_2
        }
        self.color_schemes = {
            "elevation1": "Viridis",
            "elevation2": "Cividis"
        }

    def independent_tif(self, elevation_layer):
        if elevation_layer not in self.elevation_sources:
            return px.scatter()  # Return empty plot

        # Load and process data
        gdf_elev = load_gdf(self.elevation_sources[elevation_layer])
        gdf_elev = gdf_elev.to_crs(epsg=4326)
        gdf_elev["id"] = gdf_elev.index.astype(str)
        gdf_elev["elevation_band"] = pd.to_numeric(gdf_elev["elevation_band"], errors="coerce")
        gdf_elev = gdf_elev.dropna(subset=["elevation_band"])

        # Create GeoJSON and plot
        geojson_data = json.loads(gdf_elev.to_json())
        fig = px.choropleth(
            gdf_elev,
            geojson=geojson_data,
            locations="id",
            color="elevation_band",
            color_continuous_scale=self.color_schemes[elevation_layer],
            hover_name="elevation_band",
            projection="mercator"
        )

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            margin={"r": 0, "t": 55, "l": 0, "b": 0},
            title=f"Original Elevation Data ({elevation_layer})"
        )

        return fig
