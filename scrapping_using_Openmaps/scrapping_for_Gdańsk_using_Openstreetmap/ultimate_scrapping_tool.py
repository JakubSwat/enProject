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
places = [
    "Białystok, Poland",
    "Bydgoszcz, Poland",
    "Częstochowa, Poland",
    "Gdańsk, Poland",
    "Gdynia, Poland",
    "Katowice, Poland",
    "Kraków, Poland",
    "Łódź, Poland",
    "Lublin, Poland",
    "Poznań, Poland",
    "Radom, Poland",
    "Rzeszów, Poland",
    "Szczecin, Poland",
    "Warszawa, Poland",
    "Wrocław, Poland"
]
for place in places:
    place_name = place.split(',')[0].replace(" ", "_").lower()
    # 1. Tram and bus stops
    fetch_and_process_osm_data(
        place,
        tags={'highway': 'bus_stop'},
        columns_of_interest=['name', 'highway', 'geometry'],
        filename=f"{place_name}_tram_and_bus_stops_locations.csv"
    )

    # 2. Train stops
    fetch_and_process_osm_data(
        place,
        tags={'railway': ['station', 'halt']},
        columns_of_interest=['name', 'railway', 'geometry'],
        filename=f"{place_name}_train_stops_locations.csv"
    )

    # 3. Historic places
    fetch_and_process_osm_data(
        place,
        tags={
            'amenity': [
                'cinema', 'theatre', 'arts_centre', 'nightclub', 'casino',
                'concert_hall', 'community_centre', 'karaoke_box', 'museum'
            ],
            'leisure': [
                'stadium', 'sports_centre', 'sports_hall', 'arena', 'track', 'ice_rink',
                'amusement_arcade', 'adult_gaming_centre', 'escape_game',
                'bowling_alley', 'trampoline_park', 'water_park', 'theme_park',
                'festival_grounds', 'events', 'stadium', 'amusement_park', 'fitness_centre', 'dance'
            ],
            'tourism': [
                'attraction', 'gallery', 'museum', 'artwork', 'viewpoint', 'zoo', 'theme_park'
            ]
        },
        columns_of_interest=['name', 'amenity', 'leisure', 'tourism', 'geometry'],
        filename=f"{place_name}_cultural_and_entertainment_locations.csv"
    )

    # 4. Shopping centers
    fetch_and_process_osm_data(
        place,
        tags={
            'shop': ['mall', 'supermarket', 'convenience', 'shopping_centre'],
            'amenity': ['marketplace']
        },
        columns_of_interest=['name', 'shop', 'amenity', 'geometry'],
        filename=f"{place_name}_shopping_centers_locations.csv"
    )

    # 5. Utilities
    fetch_and_process_osm_data(
        place,
        tags={
            'power': 'substation',
            'man_made': ['wastewater_plant', 'water_works', 'recycling']
        },
        columns_of_interest=['name', 'power', 'man_made', 'geometry'],
        filename=f"{place_name}_utilities_locations.csv"
    )

    # 6. Primary schools
    fetch_and_process_osm_data(
        place,
        tags={'amenity': 'school'},
        columns_of_interest=['name', 'amenity', 'geometry'],
        filename=f"{place_name}_primary_schools_locations.csv",
        extra_filter=lambda gdf: gdf[gdf['name'].str.contains('Szkoła Podstawowa', case=False, na=False)]
    )

    # 7. Preschools (Przedszkola)
    fetch_and_process_osm_data(
        place,
        tags={'amenity': ['kindergarten', 'school']},
        columns_of_interest=['name', 'amenity', 'geometry'],
        filename=f"{place_name}_preschools_locations.csv",
        extra_filter=lambda gdf: gdf[gdf['name'].str.contains('Przed', case=False, na=False)]
    )

    # 8. High schools and technical schools (excluding Przedszkola and Podstawowe)
    fetch_and_process_osm_data(
        place,
        tags={'amenity': 'school'},
        columns_of_interest=['name', 'amenity', 'geometry'],
        filename=f"{place_name}_highschools_and_others_locations.csv",
        extra_filter=lambda gdf: gdf[~gdf['name'].str.contains('Przed|Podstawo', case=False, na=False)]
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
        filename=f"{place_name}_green_spaces_locations.csv"
    )