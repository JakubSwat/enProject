import osmnx as ox
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tags for business-related areas (offices, commercial)
tags = {
    'amenity': ['office'],
    'landuse': ['commercial'],
    'building': ['office']
}

# 3. Fetch business districts and office areas from OpenStreetMap
business_areas = ox.geometries_from_place(place, tags)

# 4. Select useful columns (like name and geometry)
columns_of_interest = ['name', 'amenity', 'landuse', 'building', 'geometry']
business_areas = business_areas.reset_index()  # Reset index to keep ID info
business_areas_df = business_areas[columns_of_interest]

# 5. Drop rows without geometry
business_areas_df = business_areas_df.dropna(subset=['geometry'])

# 6. Create a GeoDataFrame
business_areas_gdf = gpd.GeoDataFrame(business_areas_df, geometry='geometry')

# 7. Show the locations of the business areas (only coordinates)
business_areas_gdf['latitude'] = business_areas_gdf['geometry'].y
business_areas_gdf['longitude'] = business_areas_gdf['geometry'].x

# 8. Show the cleaned dataset with locations (latitude and longitude)
print(business_areas_gdf[['name', 'latitude', 'longitude']].to_string(index=False))
