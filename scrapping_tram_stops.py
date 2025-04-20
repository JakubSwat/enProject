import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tags for business districts and office buildings
tags = {
    'amenity': 'office',  # offices as amenities
    'landuse': 'commercial',  # commercial land use
    'building': 'office'  # office buildings
}

# 3. Fetch business areas and office buildings from OpenStreetMap
business_areas = ox.geometries_from_place(place, tags)

# 4. Select useful columns (name, amenity, landuse, building, and geometry)
columns_of_interest = ['name', 'amenity', 'landuse', 'building', 'geometry']
business_areas = business_areas.reset_index()  # Reset index to keep ID info
business_areas_df = business_areas[columns_of_interest]

# 5. Drop rows without geometry
business_areas_df = business_areas_df.dropna(subset=['geometry'])

# 6. Create a GeoDataFrame
business_areas_gdf = gpd.GeoDataFrame(business_areas_df, geometry='geometry')

# 7. Extract latitude and longitude for each office area or business district
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

business_areas_gdf['longitude'], business_areas_gdf['latitude'] = zip(*business_areas_gdf['geometry'].apply(get_coordinates))

# 8. Prepare final table with name, amenity, landuse, building, and location data (latitude, longitude)
business_areas_locations_df = business_areas_gdf[['name', 'amenity', 'landuse', 'building', 'latitude', 'longitude']]

# 9. Show the table with business areas, office buildings, and their coordinates
print(business_areas_locations_df.to_string(index=False))
