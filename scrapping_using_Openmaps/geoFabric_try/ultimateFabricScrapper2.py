import subprocess
import os
import json
from shapely.geometry import shape
import pandas as pd

# === Konfiguracja katalogów ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PBF_DIR = os.path.join(BASE_DIR, "geofabrik_pbf_files")
DATA_DIR = os.path.join(BASE_DIR, "extracted_cities")
os.makedirs(DATA_DIR, exist_ok=True)

TEMP_DIR = os.path.join(BASE_DIR, "temp_osm_data")
os.makedirs(TEMP_DIR, exist_ok=True)

OUTPUT_BASE_DIR = os.path.join(BASE_DIR, "processed_csvs_history")
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

# === Bounding boxy dla miast ===
city_bboxes = {
    "bialystok": (23.05, 53.05, 23.25, 53.20),
    "bydgoszcz": (17.85, 53.05, 18.25, 53.20),
    "czestochowa": (19.05, 50.75, 19.25, 50.90),
    "gdansk": (18.40, 54.28, 18.75, 54.45),
    "gdynia": (18.40, 54.45, 18.60, 54.60),
    "katowice": (18.90, 50.20, 19.10, 50.35),
    "krakow": (19.75, 49.98, 20.10, 50.12),
    "lodz": (19.35, 51.70, 19.55, 51.85),
    "lublin": (22.45, 51.18, 22.65, 51.28),
    "poznan": (16.80, 52.35, 17.05, 52.50),
    "radom": (21.05, 51.35, 21.20, 51.45),
    "rzeszow": (21.95, 49.95, 22.10, 50.05),
    "szczecin": (14.45, 53.35, 14.65, 53.50),
    "warszawa": (20.85, 52.10, 21.20, 52.35),
    "wroclaw": (16.85, 51.05, 17.15, 51.20)
}

# === Lista plików historycznych (snapshots) ===
snapshots = [
    #"poland-2023-08.osm.pbf",
    #"poland-2023-09.osm.pbf",
    "poland-2023-10.osm.pbf",
    "poland-2023-11.osm.pbf",
    "poland-2023-12.osm.pbf",
    "poland-2024-01.osm.pbf",
    "poland-2024-02.osm.pbf",
    "poland-2024-03.osm.pbf",
    "poland-2024-04.osm.pbf",
    "poland-2024-05.osm.pbf",
    "poland-2024-06.osm.pbf"
]

# === Funkcje pomocnicze ===
def extract_city(pbf_file, city_name, bbox, out_dir):
    out_file = os.path.join(out_dir, f"{city_name}.osm.pbf")
    subprocess.run([
        "osmium", "extract", "-b", ",".join(map(str, bbox)),
        pbf_file, "-o", out_file, "--overwrite"
    ], check=True)
    return out_file

def osmium_filter_to_geojson(pbf_path, tag_filters, output_geojson):
    temp_filtered = output_geojson.replace(".geojson", ".osm.pbf")
    subprocess.run([
        "osmium", "tags-filter", pbf_path, "-o", temp_filtered, "--overwrite"
    ] + tag_filters, check=True)
    subprocess.run([
        "osmium", "export", temp_filtered, "-o", output_geojson, "--overwrite"
    ], check=True)

def process_category_no_gpd(city_name, tag_filters, columns_of_interest, output_filename, output_dir, extra_filter=None):
    pbf_path = os.path.join(DATA_DIR, f"{city_name}.osm.pbf")
    geojson_path = os.path.join(TEMP_DIR, f"{city_name}_{output_filename}.geojson")
    output_path = os.path.join(output_dir, output_filename)

    osmium_filter_to_geojson(pbf_path, tag_filters, geojson_path)

    if not os.path.exists(geojson_path) or os.stat(geojson_path).st_size == 0:
        print(f"[SKIP] {geojson_path} is empty.")
        return

    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = data.get('features', [])
    if not features:
        print(f"[SKIP] {output_filename} – No features found.")
        return

    rows = []
    for feat in features:
        props = feat.get('properties', {})
        geom = feat.get('geometry')
        if geom is None:
            continue
        point = shape(geom).centroid
        props['longitude'] = point.x
        props['latitude'] = point.y
        rows.append({k: props.get(k, "") for k in columns_of_interest + ['longitude', 'latitude']})

    df = pd.DataFrame(rows)
    if extra_filter:
        df = extra_filter(df)

    if df.empty:
        print(f"[SKIP] {output_filename} – No data after extra_filter.")
        return

    df.to_csv(output_path, index=False)
    print(f"[DONE] Saved {output_path}")


# === Główna pętla po snapshotach ===
for snapshot_file in snapshots:
    snapshot_name = os.path.splitext(snapshot_file)[0]  # np. poland-2023-07
    snapshot_path = os.path.join(PBF_DIR, snapshot_file)

    output_dir_snapshot = os.path.join(OUTPUT_BASE_DIR, snapshot_name)
    os.makedirs(output_dir_snapshot, exist_ok=True)

    for city, bbox in city_bboxes.items():
        print(f"\n=== Extracting {city.title()} for {snapshot_name} ===")
        extract_city(snapshot_path, city, bbox, DATA_DIR)

        print(f"=== Processing {city.title()} for {snapshot_name} ===")

        # 1. Bus & tram stops
        process_category_no_gpd(
            city,
            ['nwr/highway=bus_stop'],
            ['name', 'highway'],
            f"{city}_tram_and_bus_stops.csv",
            output_dir_snapshot
        )

        # 2. Train stops
        process_category_no_gpd(
            city,
            ['nwr/railway=station', 'nwr/railway=halt'],
            ['name', 'railway'],
            f"{city}_train_stops.csv",
            output_dir_snapshot
        )

        # 3. Cultural & entertainment
        process_category_no_gpd(
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
            f"{city}_cultural_and_entertainment.csv",
            output_dir_snapshot
        )

        # 4. Shopping
        process_category_no_gpd(
            city,
            ['nwr/shop=mall', 'nwr/shop=supermarket', 'nwr/shop=convenience',
             'nwr/shop=shopping_centre', 'nwr/amenity=marketplace'],
            ['name', 'shop', 'amenity'],
            f"{city}_shopping_centers.csv",
            output_dir_snapshot
        )

        # 5. Utilities
        process_category_no_gpd(
            city,
            ['nwr/power=substation', 'nwr/man_made=wastewater_plant',
             'nwr/man_made=water_works', 'nwr/man_made=recycling'],
            ['name', 'power', 'man_made'],
            f"{city}_utilities.csv",
            output_dir_snapshot
        )

        # 6. Primary schools
        process_category_no_gpd(
            city,
            ['nwr/amenity=school'],
            ['name', 'amenity'],
            f"{city}_primary_schools.csv",
            output_dir_snapshot,
            extra_filter=lambda df: df[df['name'].str.contains('Szkoła Podstawowa', case=False, na=False)]
        )

        # 7. Preschools
        process_category_no_gpd(
            city,
            ['nwr/amenity=kindergarten', 'nwr/amenity=school'],
            ['name', 'amenity'],
            f"{city}_preschools.csv",
            output_dir_snapshot,
            extra_filter=lambda df: df[df['name'].str.contains('Przed', case=False, na=False)]
        )

        # 8. High schools & technical schools
        process_category_no_gpd(
            city,
            ['nwr/amenity=school'],
            ['name', 'amenity'],
            f"{city}_highschools_and_others.csv",
            output_dir_snapshot,
            extra_filter=lambda df: df[~df['name'].str.contains('Przed|Podstawo', case=False, na=False)]
        )

        # 9. Green spaces
        process_category_no_gpd(
            city,
            ['nwr/leisure=park', 'nwr/leisure=garden', 'nwr/leisure=golf_course', 'nwr/leisure=nature_reserve',
             'nwr/landuse=grass', 'nwr/landuse=forest', 'nwr/landuse=meadow',
             'nwr/natural=wood', 'nwr/natural=grassland'],
            ['name', 'leisure', 'landuse', 'natural'],
            f"{city}_green_spaces.csv",
            output_dir_snapshot
        )
