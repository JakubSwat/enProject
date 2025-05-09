import osmnx as ox
import pandas as pd
import geopandas as gpd

# Score dictionary based on type
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
    """Normalize city name for filename use."""
    city = city.lower().replace("ą", "a").replace("ś", "s").replace("ł", "l").replace("ń", "n") \
                       .replace("ć", "c").replace("ó", "o").replace("ż", "z").replace("ź", "z") \
                       .replace("ę", "e")
    return city.replace(" ", "_")

def fetch_and_process_osm_data(place, tags, columns_of_interest, filename):
    # Fetch OSM data
    gdf = ox.geometries_from_place(place, tags)
    gdf = gdf.reset_index()

    # Keep only relevant columns
    existing_cols = [col for col in columns_of_interest if col in gdf.columns]
    gdf = gdf[existing_cols]
    gdf = gdf[gdf.geometry.notnull()].copy()

    # Keep only Polygon and MultiPolygon geometries
    gdf = gdf[gdf.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])]

    # Project to metric CRS for area calculation
    gdf = gdf.to_crs(epsg=3857)
    gdf["area_m2"] = gdf.geometry.area
    centroids = gdf.geometry.centroid

    # Convert centroids back to WGS84
    gdf = gdf.to_crs(epsg=4326)
    centroids_wgs84 = centroids.to_crs(epsg=4326)
    gdf['longitude'] = centroids_wgs84.x
    gdf['latitude'] = centroids_wgs84.y

    # --- Step 1: Compute average area per tag ---
    avg_area_per_type = {}
    for tag_column in ['leisure', 'landuse', 'natural']:
        subset = gdf[[tag_column, 'area_m2']].dropna()
        grouped = subset.groupby(tag_column)['area_m2'].mean()
        avg_area_per_type.update(grouped.to_dict())

    # --- Step 2: Calculate score using actual or fallback area ---
    def calculate_score(row):
        area = row['area_m2']
        for col in ['leisure', 'landuse', 'natural']:
            tag = row.get(col)
            if pd.notna(tag) and tag in type_scores:
                if area > 0:
                    return type_scores[tag] * area
                elif tag in avg_area_per_type:
                    return type_scores[tag] * avg_area_per_type[tag]
        return 0

    gdf['score'] = gdf.apply(calculate_score, axis=1)

    # Save results
    export_cols = ["name", "leisure", "landuse", "natural", "latitude", "longitude", "area_m2", "score"]
    gdf[export_cols].to_csv(filename, index=False)

    print(f"✅ Saved green spaces data to {filename}")

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
    city_normalized = enhance_dataset(place.split(',')[0])  # Clean city name for filename
    fetch_and_process_osm_data(
        place=place,
        tags={
            'leisure': ['park', 'garden', 'golf_course', 'nature_reserve'],
            'landuse': ['grass', 'forest', 'meadow'],
            'natural': ['wood', 'grassland']
        },
        columns_of_interest=['name', 'leisure', 'landuse', 'natural', 'geometry'],
        filename=f"{city_normalized}_green_spaces_locations.csv"
    )
