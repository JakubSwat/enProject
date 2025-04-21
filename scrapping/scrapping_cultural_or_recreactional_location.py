import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tags for theaters, museums, stadiums, and other entertainment facilities
tags = {
    'amenity': ['theatre', 'museum'],
    'leisure': ['stadium', 'amusement_park', 'fitness_centre', 'dance', 'water_park']
}

# 3. Fetch the relevant locations from OpenStreetMap
entertainment_places = ox.geometries_from_place(place, tags)

# 4. Select useful columns (name, amenity, leisure, and geometry)
columns_of_interest = ['name', 'amenity', 'leisure', 'geometry']
entertainment_places = entertainment_places.reset_index()  # Reset index to keep ID info
entertainment_places_df = entertainment_places[columns_of_interest]

# 5. Drop rows without geometry
entertainment_places_df = entertainment_places_df.dropna(subset=['geometry'])

# 6. Create a GeoDataFrame
entertainment_places_gdf = gpd.GeoDataFrame(entertainment_places_df, geometry='geometry')

# 7. Extract latitude and longitude for each entertainment place
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

entertainment_places_gdf['longitude'], entertainment_places_gdf['latitude'] = zip(*entertainment_places_gdf['geometry'].apply(get_coordinates))

# 8. Prepare final table with name, type of place, and location data (latitude, longitude)
entertainment_places_locations_df = entertainment_places_gdf[['name', 'amenity', 'leisure', 'latitude', 'longitude']]

# 9. Show the table with entertainment places and their coordinates
print(entertainment_places_locations_df.to_string(index=False))

#entertainment_places_locations_df.to_csv("entertainment_places_locations.csv", index=False)


#geodataframe conversion

# Create a GeoDataFrame
# entertainment_places_locations_gdf = gpd.GeoDataFrame(
#     entertainment_places_locations_df,
#     geometry=gpd.points_from_xy(entertainment_places_locations_df.longitude, entertainment_places_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# entertainment_places_locations_gdf.to_file("entertainment_places_locations_gdf.geojson", driver='GeoJSON')
