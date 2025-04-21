import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tags for schools
tags = {
    'amenity': 'school'
}

# 3. Fetch all schools
schools = ox.geometries_from_place(place, tags)

# 4. Select useful columns
columns_of_interest = ['name', 'amenity', 'geometry']
schools = schools.reset_index()
schools_df = schools[columns_of_interest]

# 5. Drop rows without geometry
schools_df = schools_df.dropna(subset=['geometry'])

# 6. Create a GeoDataFrame
schools_gdf = gpd.GeoDataFrame(schools_df, geometry='geometry')

# 7. Keep only high schools and technical schools based on name
# (filtr na "Liceum" i "Technikum")
highschools_gdf = schools_gdf[schools_gdf['name'].str.contains('Liceum|Technikum', case=False, na=False)]

# 8. Extract latitude and longitude
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

highschools_gdf['longitude'], highschools_gdf['latitude'] = zip(*highschools_gdf['geometry'].apply(get_coordinates))

# 9. Prepare final table
highschools_locations_df = highschools_gdf[['name', 'amenity', 'latitude', 'longitude']]

# 10. Show the table
print(highschools_locations_df.to_string(index=False))


#highschools_locations_df.to_csv("highschools_and_others_locations.csv", index=False)

#geodataframe conversion

# Create a GeoDataFrame
# highschools_locations_gdf = gpd.GeoDataFrame(
#     highschools_locations_df,
#     geometry=gpd.points_from_xy(highschools_locations_df.longitude, highschools_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# highschools_locations_gdf.to_file("highschools_locations_gdf.geojson", driver='GeoJSON')
