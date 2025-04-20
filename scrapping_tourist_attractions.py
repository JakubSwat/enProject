import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tags for historic landmarks, monuments, and tourist destinations
tags = {
    'historic': ['monument', 'memorial', 'castle', 'fort', 'ruins'],
    'tourism': ['attraction', 'museum', 'viewpoint', 'zoo']
}

# 3. Fetch the relevant locations from OpenStreetMap
historic_places = ox.geometries_from_place(place, tags)

# 4. Select useful columns
columns_of_interest = ['name', 'historic', 'tourism', 'geometry']
historic_places = historic_places.reset_index()  # Reset index to keep ID info
historic_places_df = historic_places[columns_of_interest]

# 5. Drop rows without geometry
historic_places_df = historic_places_df.dropna(subset=['geometry'])

# 6. Create a GeoDataFrame
historic_places_gdf = gpd.GeoDataFrame(historic_places_df, geometry='geometry')

# 7. Extract latitude and longitude
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

historic_places_gdf['longitude'], historic_places_gdf['latitude'] = zip(*historic_places_gdf['geometry'].apply(get_coordinates))

# 8. Prepare the final table
historic_places_locations_df = historic_places_gdf[['name', 'historic', 'tourism', 'latitude', 'longitude']]

# 9. Show the table
print(historic_places_locations_df.to_string(index=False))
