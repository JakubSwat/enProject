import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tags for malls, supermarkets, and essential shopping centers
tags = {
    'shop': ['mall', 'supermarket', 'convenience', 'shopping_centre'],
    'amenity': ['marketplace']
}

# 3. Fetch malls, supermarkets, and shopping centers from OpenStreetMap
shopping_centers = ox.geometries_from_place(place, tags)

# 4. Select useful columns
columns_of_interest = ['name', 'shop', 'amenity', 'geometry']
shopping_centers = shopping_centers.reset_index()  # Reset index to keep ID info
shopping_centers_df = shopping_centers[columns_of_interest]

# 5. Drop rows without geometry
before_drop = len(shopping_centers_df)
shopping_centers_df = shopping_centers_df.dropna(subset=['geometry'])
after_drop = len(shopping_centers_df)
# 6. Create a GeoDataFrame
shopping_centers_gdf = gpd.GeoDataFrame(shopping_centers_df, geometry='geometry')

# 7. Extract latitude and longitude for each shopping center
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

shopping_centers_gdf['longitude'], shopping_centers_gdf['latitude'] = zip(*shopping_centers_gdf['geometry'].apply(get_coordinates))

# 8. Prepare final table with name, type, and location data
shopping_centers_locations_df = shopping_centers_gdf[['name', 'shop', 'amenity', 'latitude', 'longitude']]

# 9. Show the table with shopping center locations and their coordinates
print(shopping_centers_locations_df.to_string(index=False))

#shopping_centers_locations_df.to_csv("shopping_centers_locations.csv", index=False)

#geodataframe conversion

# Create a GeoDataFrame
# shopping_centers_locations_gdf = gpd.GeoDataFrame(
#     shopping_centers_locations_df,
#     geometry=gpd.points_from_xy(shopping_centers_locations_df.longitude, shopping_centers_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# shopping_centers_locations_gdf.to_file("shopping_centers_locations_gdf.geojson", driver='GeoJSON')
print(f"Dropped {before_drop - after_drop} rows with missing geometry in shopping_centers_df.")