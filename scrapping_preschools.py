import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tag for educational facilities
tags = {
    'amenity': 'kindergarten'
}

# 3. Fetch schools from OpenStreetMap
schools = ox.geometries_from_place(place, tags)

# 4. Select useful columns
columns_of_interest = ['name', 'amenity', 'geometry']
schools = schools.reset_index()
schools_gdf = schools[columns_of_interest]

# 5. Drop rows without geometry
schools_gdf = schools_gdf.dropna(subset=['geometry'])

# 6. Create a GeoDataFrame
schools_gdf = gpd.GeoDataFrame(schools_gdf, geometry='geometry')

# 7. Filter only "Przedszkole"
preschools_gdf = schools_gdf[schools_gdf['name'].str.contains('Przedszkole', case=False, na=False)].copy()

# 8. Fill missing amenity values (if needed)
preschools_gdf['amenity'] = preschools_gdf['amenity'].fillna('None')

# 9. Extract latitude and longitude
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

preschools_gdf['longitude'], preschools_gdf['latitude'] = zip(*preschools_gdf['geometry'].apply(get_coordinates))

# 10. Create final table
preschools_locations_df = preschools_gdf[['name', 'amenity', 'latitude', 'longitude']]

# 11. Print the table
print(preschools_locations_df.to_string(index=False))
