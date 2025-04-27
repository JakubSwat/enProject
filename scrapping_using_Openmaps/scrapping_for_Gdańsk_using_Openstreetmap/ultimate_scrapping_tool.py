import osmnx as ox
import pandas as pd
import geopandas as gpd

def fetch_and_process_osm_data(place, tags, columns_of_interest, filename, extra_filter=None):
    # Fetch features
    data = ox.geometries_from_place(place, tags)
    data = data.reset_index()

    # Keep only desired columns
    data = data[columns_of_interest]

    # Drop rows without geometry
    before_drop = len(data)
    data = data.dropna(subset=['geometry'])
    after_drop = len(data)
    print(f"Dropped {before_drop - after_drop} rows with missing geometry in {filename}.")

    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(data, geometry='geometry')

    # Optional additional filtering (like filtering only primary schools, preschools etc.)
    if extra_filter:
        gdf = extra_filter(gdf)

    # Extract coordinates
    gdf['longitude'], gdf['latitude'] = zip(*gdf['geometry'].apply(get_coordinates))

    # Save final table
    output_columns = [col for col in columns_of_interest if col != 'geometry'] + ['latitude', 'longitude']
    gdf[output_columns].to_csv(filename, index=False)

def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

# --- MAIN CONFIGURATION ---

place = "Gdańsk, Poland"

# 1. Tram and bus stops
fetch_and_process_osm_data(
    place,
    tags={'highway': 'bus_stop'},
    columns_of_interest=['name', 'highway', 'geometry'],
    filename="tram_and_bus_stops_locations.csv"
)

# 2. Train stops
fetch_and_process_osm_data(
    place,
    tags={'railway': ['station', 'halt']},
    columns_of_interest=['name', 'railway', 'geometry'],
    filename="train_stops_locations.csv"
)

# 3. Historic places
fetch_and_process_osm_data(
    place,
    tags={
        'historic': ['monument', 'memorial', 'castle', 'fort', 'ruins'],
        'tourism': ['attraction', 'museum', 'viewpoint', 'zoo']
    },
    columns_of_interest=['name', 'historic', 'tourism', 'geometry'],
    filename="historic_places_locations.csv"
)

# 4. Shopping centers
fetch_and_process_osm_data(
    place,
    tags={
        'shop': ['mall', 'supermarket', 'convenience', 'shopping_centre'],
        'amenity': ['marketplace']
    },
    columns_of_interest=['name', 'shop', 'amenity', 'geometry'],
    filename="shopping_centers_locations.csv"
)

# 5. Utilities
fetch_and_process_osm_data(
    place,
    tags={
        'power': 'substation',
        'man_made': ['wastewater_plant', 'water_works', 'recycling']
    },
    columns_of_interest=['name', 'power', 'man_made', 'geometry'],
    filename="utilities_locations.csv"
)

# 6. Primary schools
fetch_and_process_osm_data(
    place,
    tags={'amenity': 'school'},
    columns_of_interest=['name', 'amenity', 'geometry'],
    filename="primary_schools_locations.csv",
    extra_filter=lambda gdf: gdf[gdf['name'].str.contains('Szkoła Podstawowa', case=False, na=False)]
)

# 7. Preschools (Przedszkola)
fetch_and_process_osm_data(
    place,
    tags={'amenity': ['kindergarten', 'school']},
    columns_of_interest=['name', 'amenity', 'geometry'],
    filename="preschools_locations.csv",
    extra_filter=lambda gdf: gdf[gdf['name'].str.contains('Przed', case=False, na=False)]
)

# 8. High schools and technical schools (excluding Przedszkola and Podstawowe)
fetch_and_process_osm_data(
    place,
    tags={'amenity': 'school'},
    columns_of_interest=['name', 'amenity', 'geometry'],
    filename="highschools_and_others_locations.csv",
    extra_filter=lambda gdf: gdf[~gdf['name'].str.contains('Przedszkole|Podstawowa', case=False, na=False)]
)

# 9. Green spaces
fetch_and_process_osm_data(
    place,
    tags={
        'leisure': ['park', 'garden', 'golf_course', 'nature_reserve'],
        'landuse': ['grass', 'forest', 'meadow'],
        'natural': ['wood', 'grassland']
    },
    columns_of_interest=['name', 'leisure', 'landuse', 'natural', 'geometry'],
    filename="green_spaces_locations.csv"
)

