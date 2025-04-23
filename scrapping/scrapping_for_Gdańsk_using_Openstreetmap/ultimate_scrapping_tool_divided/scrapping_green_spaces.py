import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define what types of green spaces you want
tags = {
    'leisure': ['park', 'garden', 'golf_course', 'nature_reserve'],
    'landuse': ['grass', 'forest', 'meadow'],
    'natural': ['wood', 'grassland']
}

# 3. Fetch green spaces from OpenStreetMap
green_spaces = ox.geometries_from_place(place, tags)

# 4. Select useful columns
columns_of_interest = ['name', 'leisure', 'landuse', 'natural', 'geometry']
green_spaces = green_spaces.reset_index()  # Reset index to keep ID info
green_spaces_df = green_spaces[columns_of_interest]

# 5. Drop rows without geometry
green_spaces_df = green_spaces_df.dropna(subset=['geometry'])

# 6. Create a GeoDataFrame
green_spaces_gdf = gpd.GeoDataFrame(green_spaces_df, geometry='geometry')

# 7. Cleaning Steps

# 7.1 Remove rows without name (optional)
green_spaces_gdf = green_spaces_gdf.dropna(subset=['name'])

# 7.2 Remove duplicates based on name and geometry
green_spaces_gdf = green_spaces_gdf.drop_duplicates(subset=['name', 'geometry'])

# 7.3 Fill missing leisure / landuse / natural values
green_spaces_gdf['leisure'] = green_spaces_gdf['leisure'].fillna('None')
green_spaces_gdf['landuse'] = green_spaces_gdf['landuse'].fillna('None')
green_spaces_gdf['natural'] = green_spaces_gdf['natural'].fillna('None')

# 8. Extract latitude and longitude (for both Point and Polygon/MultiPolygon)

# Function to get the coordinates (either from Point or centroid of Polygon/MultiPolygon)
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

# Apply the function to extract latitude and longitude
green_spaces_gdf['longitude'], green_spaces_gdf['latitude'] = zip(*green_spaces_gdf['geometry'].apply(get_coordinates))

# 9. Show the cleaned dataset with only location info (latitude and longitude)
green_spaces_locations_df = green_spaces_gdf[['name', 'leisure', 'landuse', 'natural', 'latitude', 'longitude']]

# 10. Print the table
print(green_spaces_locations_df.to_string(index=False))

#green_spaces_locations_df.to_csv("green_spaces_locations.csv", index=False)

#geodataframe conversion

# Create a GeoDataFrame
# green_spaces_locations_gdf = gpd.GeoDataFrame(
#     green_spaces_locations_df,
#     geometry=gpd.points_from_xy(green_spaces_locations_df.longitude, green_spaces_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# green_spaces_locations_gdf.to_file("green_spaces_locations_gdf.geojson", driver='GeoJSON')
