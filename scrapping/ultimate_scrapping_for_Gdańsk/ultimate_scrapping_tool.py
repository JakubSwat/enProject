import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Define the place you're interested in
place = "Gdańsk, Poland"

# 2. Define the tags for  tram_and_bus stops
tags = {
    'highway': 'bus_stop'  # Tags related to  tram_and_bus stops
}

# 3. Fetch  tram_and_bus stops from OpenStreetMap using the updated function
tram_and_bus_stops = ox.features_from_place(place, tags)

# 4. Select useful columns
columns_of_interest = ['name', 'highway', 'geometry']
tram_and_bus_stops =  tram_and_bus_stops.reset_index()  # Reset index to keep ID info
tram_and_bus_stops_df =  tram_and_bus_stops[columns_of_interest]

# 5. Drop rows without geometry

before_drop = len(tram_and_bus_stops_df)
tram_and_bus_stops_df =  tram_and_bus_stops_df.dropna(subset=['geometry'])
after_drop = len(tram_and_bus_stops_df)


# 6. Create a GeoDataFrame
tram_and_bus_stops_gdf = gpd.GeoDataFrame( tram_and_bus_stops_df, geometry='geometry')

# 7. Extract latitude and longitude for each  tram_and_bus stop
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

tram_and_bus_stops_gdf['longitude'],  tram_and_bus_stops_gdf['latitude'] = zip(* tram_and_bus_stops_gdf['geometry'].apply(get_coordinates))

# 8. Prepare final table with name,  tram_and_bus stop type, and location data
tram_and_bus_stops_locations_df =  tram_and_bus_stops_gdf[['name', 'highway', 'latitude', 'longitude']]

# 9. Show the table with  tram_and_bus stops and their coordinates
#print( tram_and_bus_stops_locations_df.to_string(index=False))


tram_and_bus_stops_locations_df.to_csv(" tram_and_bus_stops_locations.csv", index=False)

#geodataframe conversion

# Create a GeoDataFrame
#  tram_and_bus_stops_locations_gdf = gpd.GeoDataFrame(
#      tram_and_bus_stops_locations_df,
#     geometry=gpd.points_from_xy( tram_and_bus_stops_locations_df.longitude,  tram_and_bus_stops_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
#  tram_and_bus_stops_locations_gdf.to_file(" tram_and_bus_stops_locations_gdf.geojson", driver='GeoJSON')
print(f"Dropped {before_drop - after_drop} rows with missing geometry in tram_and_bus_stops_df.")
# 2. Define the tags for train stops
tags = {
    'railway': ['station', 'halt']
}

# 3. Fetch train stops from OpenStreetMap
train_stops = ox.geometries_from_place(place, tags)

# 4. Select useful columns
columns_of_interest = ['name', 'railway', 'geometry']
train_stops = train_stops.reset_index()  # Reset index to keep ID info
train_stops_df = train_stops[columns_of_interest]

# 5. Drop rows without geometry

before_drop = len(train_stops_df)
train_stops_df = train_stops_df.dropna(subset=['geometry'])
after_drop = len(train_stops_df)
# 6. Create a GeoDataFrame
train_stops_gdf = gpd.GeoDataFrame(train_stops_df, geometry='geometry')

# 7. Extract latitude and longitude for each train stop
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

train_stops_gdf['longitude'], train_stops_gdf['latitude'] = zip(*train_stops_gdf['geometry'].apply(get_coordinates))

# 8. Prepare final table with name, railway type, and location data
train_stops_locations_df = train_stops_gdf[['name', 'railway', 'latitude', 'longitude']]

# 9. Show the table with train stops and their coordinates
#print(train_stops_locations_df.to_string(index=False))

train_stops_locations_df.to_csv("train_stops_locations.csv", index=False)

#geodataframe conversion

# Create a GeoDataFrame
#  tram_and_bus_stops_locations_gdf = gpd.GeoDataFrame(
#     train_stops_locations_df,
#     geometry=gpd.points_from_xy(train_stops_locations_df.longitude, train_stops_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# train_stops_locations_gdf.to_file("train_stops_locations_gdf.geojson", driver='GeoJSON')
print(f"Dropped {before_drop - after_drop} rows with missing geometry in train_stops_df.")
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


before_drop = len(historic_places_df)
historic_places_df = historic_places_df.dropna(subset=['geometry'])
after_drop = len(historic_places_df)
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


historic_places_gdf['longitude'], historic_places_gdf['latitude'] = zip(
    *historic_places_gdf['geometry'].apply(get_coordinates))

# 8. Prepare the final table
historic_places_locations_df = historic_places_gdf[['name', 'historic', 'tourism', 'latitude', 'longitude']]

# 9. Show the table
##print(historic_places_locations_df.to_string(index=False))

historic_places_locations_df.to_csv("historic_places_locations.csv", index=False)

#geodataframe conversion

# Create a GeoDataFrame
# historic_places_locations_gdf = gpd.GeoDataFrame(
#     historic_places_locations_df,
#     geometry=gpd.points_from_xy(historic_places_locations_df.longitude, historic_places_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# historic_places_locations_gdf.to_file("historic_places_locations_gdf.geojson", driver='GeoJSON')
print(f"Dropped {before_drop - after_drop} rows with missing geometry in historic_places_df.")
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
#print(shopping_centers_locations_df.to_string(index=False))

shopping_centers_locations_df.to_csv("shopping_centers_locations.csv", index=False)

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


before_drop = len(utilities_df)
utilities_df = utilities_df.dropna(subset=['geometry'])
after_drop = len(utilities_df)

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
#print(utilities_locations_df.to_string(index=False))

utilities_locations_df.to_csv("utilities_locations.csv", index=False)

#geodataframe conversion

# Create a GeoDataFrame
# utilities_locations_gdf = gpd.GeoDataFrame(
#     utilities_locations_df,
#     geometry=gpd.points_from_xy(utilities_locations_df.longitude, utilities_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# utilities_locations_gdf.to_file("utilities_locations_gdf.geojson", driver='GeoJSON')
print(f"Dropped {before_drop - after_drop} rows with missing geometry in utilities_locations_df.")

# 2. Definiujemy tagi dla szkół
tags = {
    'amenity': 'school'
}

# 3. Pobieramy wszystkie szkoły z OpenStreetMap
schools = ox.geometries_from_place(place, tags)

# 4. Wybieramy potrzebne kolumny
columns_of_interest = ['name', 'amenity', 'geometry']
schools = schools.reset_index()
schools_df = schools[columns_of_interest]

# 5. Usuwamy rekordy bez geometrii

before_drop = len(schools_df)
schools_df = schools_df.dropna(subset=['geometry'])
after_drop = len(schools_df)

print(f"Dropped {before_drop - after_drop} rows with missing geometry in schools_df.")


# 6. Tworzymy GeoDataFrame
schools_gdf = gpd.GeoDataFrame(schools_df, geometry='geometry')


# 7. Czyszczenie danych

# 7.2 Usuwamy duplikaty
schools_gdf = schools_gdf.drop_duplicates(subset=['name', 'geometry'])

# 7.3 Uzupełniamy brakujące 'amenity'
schools_gdf['amenity'] = schools_gdf['amenity'].fillna('None')

# 8. FILTR - tylko "Szkoła Podstawowa" w nazwie
primary_schools_gdf = schools_gdf[schools_gdf['name'].str.contains('Szkoła Podstawowa', case=False, na=False)].copy()


# 9. Funkcja do wyciągania współrzędnych
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

# 10. Wyciągamy longitude i latitude
primary_schools_gdf['longitude'], primary_schools_gdf['latitude'] = zip(*primary_schools_gdf['geometry'].apply(get_coordinates))

# 11. Przygotowujemy finalną tabelę
primary_schools_locations_df = primary_schools_gdf[['name', 'amenity', 'latitude', 'longitude']]

# 12. Wyświetlamy tabelę
#print(primary_schools_locations_df.to_string(index=False))

primary_schools_locations_df.to_csv("primary_schools_locations.csv", index=False)

#geodataframe conversion

# Create a GeoDataFrame
# primary_schools_locations_gdf = gpd.GeoDataFrame(
#     primary_schools_locations_df,
#     geometry=gpd.points_from_xy(primary_schools_locations_df.longitude, primary_schools_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# primary_schools_locations_gdf.to_file("primary_schools_locations_gdf.geojson", driver='GeoJSON')

# 2. Define the tag for educational facilities
tags = {
    'amenity': ['kindergarten','school']
}

# 3. Fetch schools from OpenStreetMap
schools = ox.geometries_from_place(place, tags)

# 4. Select useful columns
columns_of_interest = ['name', 'amenity', 'geometry']
schools = schools.reset_index()
schools_gdf = schools[columns_of_interest]

# 5. Drop rows without geometry

before_drop = len(schools_gdf)
schools_gdf = schools_df.dropna(subset=['geometry'])
after_drop = len(schools_gdf)
print(f"Dropped {before_drop - after_drop} rows with missing geometry in kindergarten_gdf.")

# 6. Create a GeoDataFrame
schools_gdf = gpd.GeoDataFrame(schools_gdf, geometry='geometry')
# 7. keep Przedszkole only
schools_gdf = schools_gdf[schools_gdf['name'].str.contains('Przed', case=False, na=False)]

# 9. Extract latitude and longitude
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

schools_gdf['longitude'], schools_gdf['latitude'] = zip(*schools_gdf['geometry'].apply(get_coordinates))

# 10. Create final table
preschools_locations_df = schools_gdf[['name', 'amenity', 'latitude', 'longitude']]

# 11. Print the table
#print(preschools_locations_df.to_string(index=False))

preschools_locations_df.to_csv("preschools_locations.csv", index=False)

#geodataframe conversion

# Create a GeoDataFrame
# preschools_locations_gdf = gpd.GeoDataFrame(
#     preschools_locations_df,
#     geometry=gpd.points_from_xy(preschools_locations_df.longitude, preschools_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# preschools_locations_gdf.to_file("preschools_locations_gdf.geojson", driver='GeoJSON')

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
before_drop = len(schools_df)
schools_df = schools_df.dropna(subset=['geometry'])
after_drop = len(schools_df)
print(f"Dropped {before_drop - after_drop} rows with missing geometry in schools/highschools_df.")
# 6. Create a GeoDataFrame
schools_gdf = gpd.GeoDataFrame(schools_df, geometry='geometry')

# 7. Keep only high schools and technical schools based on name
# (filtr na "Liceum" i "Technikum")
highschools_gdf = schools_gdf[~schools_gdf['name'].str.contains('Przedszkole|Podstawowa', case=False, na=False)]

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
#print(highschools_locations_df.to_string(index=False))


highschools_locations_df.to_csv("highschools_and_others_locations.csv", index=False)

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
before_drop = len(green_spaces_df)
green_spaces_df = green_spaces_df.dropna(subset=['geometry'])
after_drop = len(green_spaces_df)
print('Dropped ', before_drop - after_drop, 'rows with missing geometry in green_spaces_df.')
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
#print(green_spaces_locations_df.to_string(index=False))

green_spaces_locations_df.to_csv("green_spaces_locations.csv", index=False)

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
before_drop = len(entertainment_places_df)
entertainment_places_df = entertainment_places_df.dropna(subset=['geometry'])
after_drop = len(entertainment_places_df)
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
#print(entertainment_places_locations_df.to_string(index=False))

entertainment_places_locations_df.to_csv("entertainment_places_locations.csv", index=False)


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
print(f"Dropped {before_drop - after_drop} rows with missing geometry in entertainment_places_locations_df.")

