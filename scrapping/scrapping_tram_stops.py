import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tags for tram stops
tags = {
    'highway': 'tram_stop'# Tags related to tram stops
}

# 3. Fetch tram stops from OpenStreetMap using the updated function
tram_stops = ox.features_from_place(place, tags)

# 4. Select useful columns
columns_of_interest = ['name', 'highway', 'geometry']
tram_stops = tram_stops.reset_index()  # Reset index to keep ID info
tram_stops_df = tram_stops[columns_of_interest]

# 5. Drop rows without geometry
tram_stops_df = tram_stops_df.dropna(subset=['geometry'])

# 6. Create a GeoDataFrame
tram_stops_gdf = gpd.GeoDataFrame(tram_stops_df, geometry='geometry')

# 7. Extract latitude and longitude for each tram stop
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

tram_stops_gdf['longitude'], tram_stops_gdf['latitude'] = zip(*tram_stops_gdf['geometry'].apply(get_coordinates))

# 8. Prepare final table with name, tram stop type, and location data
tram_stops_locations_df = tram_stops_gdf[['name', 'highway', 'latitude', 'longitude']]

# 9. Show the table with tram stops and their coordinates
print(tram_stops_locations_df.to_string(index=False))


#tram_stops_locations_df.to_csv("tram_stops_locations.csv", index=False)

#geodataframe conversion

# Create a GeoDataFrame
# tram_stops_locations_gdf = gpd.GeoDataFrame(
#     tram_stops_locations_df,
#     geometry=gpd.points_from_xy(tram_stops_locations_df.longitude, tram_stops_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# tram_stops_locations_gdf.to_file("tram_stops_locations_gdf.geojson", driver='GeoJSON')
