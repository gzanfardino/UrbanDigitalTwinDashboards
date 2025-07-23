import geopandas as gpd
import requests
import io
import os
import time
import pandas as pd

DATA_PATH = "all_buildings.geojson"

def download_all_buildings_cached(data_path=DATA_PATH):
    # If cached file exists, load it directly
    if os.path.exists(data_path):
        print(f"📂 Loading cached data from {data_path}")
        return gpd.read_file(data_path)

    base_url = "http://wms.pcn.minambiente.it/ogc"
    params = {
        "map": "/ms_ogc/wfs/Edifici.map",
        "service": "WFS",
        "version": "1.1.0",
        "request": "GetFeature",
        "typeName": "ED.EDIFICATO.CAPOLUOGHI.",
        "outputFormat": "text/xml; subtype=gml/3.1.1",
        "maxFeatures": "500",
    }

    all_gdfs = []
    start = 0

    while True:
        print(f"Downloading batch starting at index {start}...")
        params["startIndex"] = start
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            print(f"❌ Request failed with status code {response.status_code}")
            break

        try:
            gdf = gpd.read_file(io.BytesIO(response.content))
        except Exception as e:
            print(f"⚠️ Failed to read GML at startIndex={start}: {e}")
            break

        if gdf.empty:
            print("✅ No more features to load.")
            break

        all_gdfs.append(gdf)
        start += 500
        time.sleep(1)  # Be kind to the server

    full_gdf = gpd.GeoDataFrame(pd.concat(all_gdfs, ignore_index=True))
    full_gdf.to_file(data_path, driver="GeoJSON")
    print(f"✅ Saved full dataset locally to {data_path}")

    return full_gdf


# Usage example:
gdf_all = download_all_buildings_cached()

# Filter for Prato province
gdf_prato = gdf_all[gdf_all["provincia"].str.upper() == "PRATO"]
print(f"Buildings in Prato: {len(gdf_prato)}")

# Optionally save filtered data for faster access
gdf_prato.to_file("prato_buildings.geojson", driver="GeoJSON")
