import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tags for business districts, commercial areas, or offices
tags = {
    'landuse': ['commercial', 'industrial'],  # Business or industrial areas
    'building': ['office', 'commercial'],     # Office or commercial buildings
    'amenity': ['office'],                    # Offices as amenities          # Shops as part of commercial hubs
}

# 3. Fetch business-related locations from OpenStreetMap
employment_hubs = ox.features_from_place(place, tags)

# 4. Select useful columns (e.g., name, type, geometry)
columns_of_interest = ['name', 'landuse', 'building', 'amenity', 'shop', 'geometry']
employment_hubs = employment_hubs.reset_index()  # Reset index to keep ID info
employment_hubs_df = employment_hubs[columns_of_interest]

# 5. Drop rows without geometry
employment_hubs_df = employment_hubs_df.dropna(subset=['geometry'])

# 6. Create a GeoDataFrame
employment_hubs_gdf = gpd.GeoDataFrame(employment_hubs_df, geometry='geometry')

# 7. Extract latitude and longitude for each employment hub
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

employment_hubs_gdf['longitude'], employment_hubs_gdf['latitude'] = zip(*employment_hubs_gdf['geometry'].apply(get_coordinates))

# 8. Prepare final table with name, type, and location data
employment_hubs_locations_df = employment_hubs_gdf[['name', 'landuse', 'building', 'amenity', 'shop', 'latitude', 'longitude']]

# 9. Show the table with employment hubs and their coordinates
print(employment_hubs_locations_df.to_string(index=False))

#employment_hubs_locations_df.to_csv("employment_hubs_locations.csv", index=False)

#geodataframe conversion
# Create a GeoDataFrame
# employment_hubs_locations_gdf = gpd.GeoDataFrame(
#     employment_hubs_locations_df,
#     geometry=gpd.points_from_xy(employment_hubs_locations_df.longitude, employment_hubs_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# employment_hubs_locations_gdf.to_file("employment_hubs_locations_gdf.geojson", driver='GeoJSON')
