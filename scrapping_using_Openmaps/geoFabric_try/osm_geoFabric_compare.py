import pandas as pd

# Ścieżki do plików
file_osm = "/home/jakubswat/PycharmProjects/enProject/scrapping_using_Openmaps/geoFabric_try/processed_csvs/gdansk_utilities_locations.csv"
file_geofabric = "/home/jakubswat/PycharmProjects/enProject/scrapping_using_Openmaps/scrapping_for_Gdańsk_using_Openstreetmap/gdansk_utilities_locations.csv"

# Wczytanie CSV
df_osm = pd.read_csv(file_osm)
df_gf = pd.read_csv(file_geofabric)
print(len(df_osm))
print(len(df_gf))
# Porównanie nazw obiektów
names_osm = set(df_osm['name'])
names_gf = set(df_gf['name'])

# Sprawdzenie duplikatów według nazwy
duplicates = df_gf[df_gf.duplicated(subset=['name'], keep=False)]
print("Powtarzające się nazwy:")
print(duplicates)
print("Liczba powtórzeń:", len(duplicates))



# Elementy tylko w OSM
only_in_osm = names_osm - names_gf
print("Tylko w OSM:", only_in_osm)
print(len(only_in_osm))

# Elementy tylko w GeoFabric
only_in_gf = names_gf - names_osm
print("Tylko w GeoFabric:", only_in_gf)
print(len(only_in_gf))

# Elementy wspólne
common = names_osm & names_gf
print("Wspólne elementy:", common)
print(len(common))

