import osmnx as ox
import pandas as pd
import geopandas as gpd

# 1. Wybieramy miejsce
place = "Gdańsk, Poland"

# 2. Definiujemy tagi dla przystanków autobusowych
tags = {
    'highway': 'bus_stop'
}

# 3. Pobieramy przystanki autobusowe z OpenStreetMap
bus_stops = ox.geometries_from_place(place, tags)

# 4. Wybieramy najważniejsze kolumny
columns_of_interest = ['name', 'highway', 'geometry']
bus_stops = bus_stops.reset_index()
bus_stops_df = bus_stops[columns_of_interest]

# 5. Usuwamy rekordy bez geometrii
bus_stops_df = bus_stops_df.dropna(subset=['geometry'])

# 6. Tworzymy GeoDataFrame
bus_stops_gdf = gpd.GeoDataFrame(bus_stops_df, geometry='geometry')

# 7. Czyszczenie danych

# 7.1 Opcjonalnie: usuwamy przystanki bez nazwy
bus_stops_gdf = bus_stops_gdf.dropna(subset=['name'])

# 7.2 Usuwamy duplikaty
bus_stops_gdf = bus_stops_gdf.drop_duplicates(subset=['name', 'geometry'])

# 7.3 Uzupełniamy brakujące highway
bus_stops_gdf['highway'] = bus_stops_gdf['highway'].fillna('None')

# 8. Funkcja do wyciągania współrzędnych
def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

# 9. Wyciągamy longitude i latitude
bus_stops_gdf['longitude'], bus_stops_gdf['latitude'] = zip(*bus_stops_gdf['geometry'].apply(get_coordinates))

# 10. Przygotowujemy finalną tabelę
bus_stops_locations_df = bus_stops_gdf[['name', 'highway', 'latitude', 'longitude']]

# 11. Wyświetlamy tabelę
print(bus_stops_locations_df.to_string(index=False))

#bus_stops_locations_df.to_csv("bus_stops_locations.csv", index=False)

#geodataframe conversion

# Create a GeoDataFrame
# bus_stops_locations_gdf = gpd.GeoDataFrame(
#     bus_stops_locations_df,
#     geometry=gpd.points_from_xy(bus_stops_locations_df.longitude, bus_stops_locations_df.latitude),
#     crs="EPSG:4326"  # WGS84 coordinate reference system (standard for GPS)
# )
#
# # Save to GeoJSON
# bus_stops_locations_gdf.to_file("bus_stops_locations_gdf.geojson", driver='GeoJSON')
