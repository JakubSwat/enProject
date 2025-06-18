import os
import glob
import osmnx as ox
import pandas as pd
import geopandas as gpd

# Your score dictionary and helper functions here (reuse your code)
type_scores = {
    'park': 1.0,
    'nature_reserve': 1.0,
    'garden': 0.8,
    'forest': 0.8,
    'golf_course': 0.5,
    'meadow': 0.5,
    'wood': 0.7,
    'grassland': 0.7,
    'grass': 0.7
}


def enhance_dataset(city):
    city = city.lower().replace("ą", "a").replace("ś", "s").replace("ł", "l").replace("ń", "n") \
        .replace("ć", "c").replace("ó", "o").replace("ż", "z").replace("ź", "z") \
        .replace("ę", "e")
    return city.replace(" ", "_")


def fetch_and_process_osm_data(place, tags, columns_of_interest, filename):
    gdf = ox.geometries_from_place(place, tags)
    gdf = gdf.reset_index()

    existing_cols = [col for col in columns_of_interest if col in gdf.columns]
    gdf = gdf[existing_cols]
    gdf = gdf[gdf.geometry.notnull()].copy()
    gdf = gdf[gdf.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])]

    gdf = gdf.to_crs(epsg=3857)
    gdf["area_m2"] = gdf.geometry.area
    centroids = gdf.geometry.centroid

    gdf = gdf.to_crs(epsg=4326)
    centroids_wgs84 = centroids.to_crs(epsg=4326)
    gdf['longitude'] = centroids_wgs84.x
    gdf['latitude'] = centroids_wgs84.y

    avg_area_per_type = {}
    for tag_column in ['leisure', 'landuse', 'natural']:
        subset = gdf[[tag_column, 'area_m2']].dropna(subset=['area_m2'])
        grouped = subset.groupby(tag_column)['area_m2'].mean().dropna()
        avg_area_per_type.update(grouped.to_dict())

    def calculate_score(row):
        area = row['area_m2']
        for col in ['leisure', 'landuse', 'natural']:
            tag = row.get(col)
            if pd.notna(tag) and tag in type_scores:
                if pd.notna(area) and area > 0:
                    return type_scores[tag] * area
                elif tag in avg_area_per_type and not pd.isna(avg_area_per_type[tag]):
                    return type_scores[tag] * avg_area_per_type[tag]
                else:
                    return 0
        return 0

    gdf['score'] = gdf.apply(calculate_score, axis=1)

    export_cols = ["name", "leisure", "landuse", "natural", "latitude", "longitude", "area_m2", "score"]
    print(f"Overwriting file: {filename}")
    gdf[export_cols].to_csv(filename, index=False)


# Directory where your green space CSV files are located
directory_path = '/Users/filiporlikowski/Documents/enProject/scrapping_using_Openmaps/scrapping_for_Gdańsk_using_Openstreetmap/'

# Find all files ending with "_green_spaces_locations.csv"
files_to_process = glob.glob(os.path.join(directory_path, '*_green_spaces_locations.csv'))

# For each file, extract city name from filename and update file
for file_path in files_to_process:
    # Extract the city name from the filename
    basename = os.path.basename(file_path)
    city_part = basename.split('_green_spaces_locations.csv')[0]

    # Create the place name assuming "City, Poland"
    place_name = city_part.replace('_', ' ').title() + ", Poland"

    print(f"Processing city: {place_name} from file: {basename}")

    fetch_and_process_osm_data(
        place=place_name,
        tags={
            'leisure': ['park', 'garden', 'golf_course', 'nature_reserve'],
            'landuse': ['grass', 'forest', 'meadow'],
            'natural': ['wood', 'grassland']
        },
        columns_of_interest=['name', 'leisure', 'landuse', 'natural', 'geometry'],
        filename=file_path  # overwrite same file
    )
