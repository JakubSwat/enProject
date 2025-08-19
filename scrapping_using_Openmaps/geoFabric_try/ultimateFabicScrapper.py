import subprocess
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon, MultiPolygon

# Set your data directory (where the .osm.pbf files are stored)

BASE_DIR = os.getcwd()
PBF_FILE = os.path.join(BASE_DIR, "geofabrik_pbf_files", "poland.osm.pbf")

DATA_DIR = "/mnt/c/Users/Jakub Swat/Desktop/_/Dokumenty Studia/Inżynierka/geoScraper/scrapping_using_Openmaps/geoFabric_try/geofabrik_pbf_files"
TEMP_DIR = "/mnt/c/Users/Jakub Swat/Desktop/_/Dokumenty Studia/Inżynierka/geoScraper/scrapping_using_Openmaps/geoFabric_try/temp_osm_data"
OUTPUT_DIR = "/mnt/c/Users/Jakub Swat/Desktop/_/Dokumenty Studia/Inżynierka/geoScraper/scrapping_using_Openmaps/geoFabric_try/processed_csvs"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_coordinates(geometry):
    if geometry.geom_type == 'Point':
        return geometry.x, geometry.y
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.centroid.x, geometry.centroid.y
    else:
        return None, None

def osmium_filter_to_geojson(pbf_path, tag_filters, output_path):
    filter_args = []
    for tag in tag_filters:
        filter_args += ["--overwrite", "-f", "geojson", pbf_path, "tags-filter", "-o", output_path] + tag_filters
    subprocess.run(["osmium", "tags-filter", "-o", output_path, pbf_path] + tag_filters, check=True)

def process_category(city_name, tag_filters, columns_of_interest, output_filename, extra_filter=None):
    pbf_path = os.path.join(DATA_DIR, f"{city_name}.osm.pbf")
    geojson_path = os.path.join(TEMP_DIR, f"{city_name}_{output_filename}.geojson")
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # 1. Filter .osm.pbf using osmium
    osmium_filter_to_geojson(pbf_path, tag_filters, geojson_path)

    # 2. Read into GeoDataFrame
    if not os.path.exists(geojson_path) or os.stat(geojson_path).st_size == 0:
        print(f"[SKIP] {geojson_path} is empty.")
        return
    gdf = gpd.read_file(geojson_path)

    if gdf.empty:
        print(f"[SKIP] {output_filename} – No features found.")
        return

    # 3. Keep only relevant columns
    gdf = gdf[['geometry'] + [col for col in columns_of_interest if col in gdf.columns]]

    # 4. Drop rows without geometry
    gdf = gdf.dropna(subset=['geometry'])

    # 5. Optional filtering
    if extra_filter:
        gdf = extra_filter(gdf)

    # 6. Get coordinates
    gdf['longitude'], gdf['latitude'] = zip(*gdf['geometry'].apply(get_coordinates))

    # 7. Save CSV
    final_cols = [col for col in columns_of_interest if col != 'geometry'] + ['latitude', 'longitude']
    gdf[final_cols].to_csv(output_path, index=False)
    print(f"[DONE] Saved {output_filename}")

# --- City loop ---
cities = [
    #"bialystok", "bydgoszcz", "czestochowa",
    "gdansk"#,
    #"gdynia",
    #"katowice", "krakow", "lodz", "lublin", "poznan",
    #"radom", "rzeszow", "szczecin", "warszawa", "wroclaw"
]

for city in cities:
    print(f"\n=== Processing {city.title()} ===")

    # 1. Bus & tram stops
    process_category(
        city,
        ['nwr/highway=bus_stop'],
        ['name', 'highway'],
        f"{city}_tram_and_bus_stops_locations.csv"
    )

    # 2. Train stops
    process_category(
        city,
        ['nwr/railway=station', 'nwr/railway=halt'],
        ['name', 'railway'],
        f"{city}_train_stops_locations.csv"
    )

    # 3. Cultural & entertainment
    process_category(
        city,
        [
            'nwr/amenity=cinema', 'nwr/amenity=theatre', 'nwr/amenity=arts_centre',
            'nwr/amenity=nightclub', 'nwr/amenity=casino', 'nwr/amenity=concert_hall',
            'nwr/amenity=community_centre', 'nwr/amenity=karaoke_box', 'nwr/amenity=museum',
            'nwr/leisure=stadium', 'nwr/leisure=sports_centre', 'nwr/leisure=arena',
            'nwr/leisure=track', 'nwr/leisure=ice_rink', 'nwr/leisure=amusement_arcade',
            'nwr/leisure=trampoline_park', 'nwr/leisure=theme_park',
            'nwr/tourism=attraction', 'nwr/tourism=gallery', 'nwr/tourism=zoo'
        ],
        ['name', 'amenity', 'leisure', 'tourism'],
        f"{city}_cultural_and_entertainment_locations.csv"
    )

    # 4. Shopping
    process_category(
        city,
        ['nwr/shop=mall', 'nwr/shop=supermarket', 'nwr/shop=convenience', 'nwr/shop=shopping_centre', 'nwr/amenity=marketplace'],
        ['name', 'shop', 'amenity'],
        f"{city}_shopping_centers_locations.csv"
    )

    # 5. Utilities
    process_category(
        city,
        ['nwr/power=substation', 'nwr/man_made=wastewater_plant', 'nwr/man_made=water_works', 'nwr/man_made=recycling'],
        ['name', 'power', 'man_made'],
        f"{city}_utilities_locations.csv"
    )

    # 6. Primary schools
    process_category(
        city,
        ['nwr/amenity=school'],
        ['name', 'amenity'],
        f"{city}_primary_schools_locations.csv",
        extra_filter=lambda gdf: gdf[gdf['name'].str.contains('Szkoła Podstawowa', case=False, na=False)]
    )

    # 7. Preschools
    process_category(
        city,
        ['nwr/amenity=kindergarten', 'nwr/amenity=school'],
        ['name', 'amenity'],
        f"{city}_preschools_locations.csv",
        extra_filter=lambda gdf: gdf[gdf['name'].str.contains('Przed', case=False, na=False)]
    )

    # 8. High schools & technical schools
    process_category(
        city,
        ['nwr/amenity=school'],
        ['name', 'amenity'],
        f"{city}_highschools_and_others_locations.csv",
        extra_filter=lambda gdf: ~gdf['name'].str.contains('Przed|Podstawo', case=False, na=False)
    )

    # 9. Green spaces
    process_category(
        city,
        ['nwr/leisure=park', 'nwr/leisure=garden', 'nwr/leisure=golf_course', 'nwr/leisure=nature_reserve',
         'nwr/landuse=grass', 'nwr/landuse=forest', 'nwr/landuse=meadow',
         'nwr/natural=wood', 'nwr/natural=grassland'],
        ['name', 'leisure', 'landuse', 'natural'],
        f"{city}_green_spaces_locations.csv"
    )
