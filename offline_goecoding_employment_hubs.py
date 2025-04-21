import geopandas as gpd
from shapely.geometry import Point
from geopandas.tools import sjoin_nearest
from pathlib import Path
import pandas as pd

## 1. Load your incomplete dataset
your_data = gpd.read_file("employment_hubs_locations_gdf.geojson")

folder_path = Path("pomorskie-latest-free")

# 2. List all .shp files you want to use
shapefiles = [
    "gis_osm_landuse_a_free_1.shp",
    "gis_osm_buildings_a_free_1.shp",
    "gis_osm_pois_a_free_1.shp",
    "gis_osm_pois_free_1.shp",
    "gis_osm_places_a_free_1.shp"
]

# 3. Load and combine them safely
known_places_list = []
for shp in shapefiles:
    gdf = gpd.read_file(folder_path / shp, rows=1000)
    if 'name' not in gdf.columns:
        gdf['name'] = None
    known_places_list.append(gdf)

known_places = gpd.GeoDataFrame(pd.concat(known_places_list, ignore_index=True))

# 4. Project into projected CRS
your_data = your_data.to_crs("EPSG:2180")
known_places = known_places.to_crs("EPSG:2180")

# 5. Find nearest
matched = sjoin_nearest(
    your_data,
    known_places[['geometry', 'name']],
    how="left",
    distance_col="dist_to_known_place"
)

# 6. Fill missing names
if "name_right" in matched.columns:
    if "name" not in matched.columns:
        matched["name"] = matched["name_right"]
    else:
        matched["name"] = matched["name"].fillna(matched["name_right"])
    matched = matched.drop(columns=["name_right", "dist_to_known_place"])
else:
    print("Warning: No 'name_right' found!")

# 7. Reproject back
matched = matched.to_crs("EPSG:4326")

# 8. Save
matched.to_file("work_offices.geojson", driver="GeoJSON")
