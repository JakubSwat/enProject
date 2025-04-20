import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tags for train stops
tags = {
    'railway': ['station', 'halt']
}

# 3. Fetch train stops from OpenStreetMap
train_stops = ox.geometries_from_place(place, tags)

# 4. Select useful columns
columns_of_interest = ['name', 'railway', 'geometry']
train_stops = train_stops.reset_index()  # Reset index to keep ID info
train_stops_df = train_stops[columns_of_interest]

# 5. Drop rows without geometry
train_stops_df = train_stops_df.dropna(subset=['geometry'])

# 6. Create a GeoDataFrame
train_stops_gdf = gpd.GeoDataFrame(train_stops_df, geometry='geometry')

# 7. Extract latitude and longitude for each train stop
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

train_stops_gdf['longitude'], train_stops_gdf['latitude'] = zip(*train_stops_gdf['geometry'].apply(get_coordinates))

# 8. Prepare final table with name, railway type, and location data
train_stops_locations_df = train_stops_gdf[['name', 'railway', 'latitude', 'longitude']]

# 9. Show the table with train stops and their coordinates
print(train_stops_locations_df.to_string(index=False))
