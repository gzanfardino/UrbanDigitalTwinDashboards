import geopandas as gpd

# Spatial join and filter
def spatial_join_elevation(gdf_shp, gdf_elev, elevation_col='elevation_band'):
    gdf_elev = gdf_elev.dropna(subset=[elevation_col])
    gdf_elev = gdf_elev.to_crs(gdf_shp.crs)
    joined = gpd.sjoin(gdf_shp, gdf_elev[['geometry', elevation_col]], how="left", predicate="intersects")
    return joined
