import geopandas as gpd


# Load and project GeoDataFrame
def load_gdf(shapefile_path, crs_epsg=4326):
    gdf = gpd.read_file(shapefile_path)
    return gdf.to_crs(epsg=crs_epsg)
