import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Wybieramy miejsce
place = "Gdańsk, Poland"

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
schools_df = schools_df.dropna(subset=['geometry'])

# 6. Tworzymy GeoDataFrame
schools_gdf = gpd.GeoDataFrame(schools_df, geometry='geometry')

# 7. Czyszczenie danych

# 7.1 Usuwamy szkoły bez nazwy
schools_gdf = schools_gdf.dropna(subset=['name'])

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
print(primary_schools_locations_df.to_string(index=False))
