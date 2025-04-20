import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tags for utility infrastructure
tags = {
    'power': 'substation',
    'man_made': ['wastewater_plant', 'water_works', 'recycling']
}

# 3. Fetch the relevant locations from OpenStreetMap
utilities = ox.geometries_from_place(place, tags)

# 4. Select useful columns
columns_of_interest = ['name', 'power', 'man_made', 'geometry']
utilities = utilities.reset_index()  # Reset index to keep ID info
utilities_df = utilities[columns_of_interest]

# 5. Drop rows without geometry
utilities_df = utilities_df.dropna(subset=['geometry'])

# 6. Create a GeoDataFrame
utilities_gdf = gpd.GeoDataFrame(utilities_df, geometry='geometry')

# 7. Extract latitude and longitude
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

utilities_gdf['longitude'], utilities_gdf['latitude'] = zip(*utilities_gdf['geometry'].apply(get_coordinates))

# 8. Prepare the final table
utilities_locations_df = utilities_gdf[['name', 'power', 'man_made', 'latitude', 'longitude']]

# 9. Show the table
print(utilities_locations_df.to_string(index=False))

utilities_locations_df.to_csv("utilities_locations.csv", index=False)