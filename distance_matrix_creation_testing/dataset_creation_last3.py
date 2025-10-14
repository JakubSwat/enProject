import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import glob
import os
import re

# -----------------------------
# Haversine formula (vectorized)
# -----------------------------
def haversine_vectorized(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c


# -----------------------------
# Directories
# -----------------------------
property_dir = '/Users/filiporlikowski/Documents/EngeneeringProject/KaggleDataset'
poi_dir = '/Users/filiporlikowski/Documents/EngeneeringProject/scrapping_using_Openmaps/geoFabric_try/processed_csvs_history'
fallback_poi_dir = '/Users/filiporlikowski/Documents/EngeneeringProject/scrapping_using_Openmaps/scrapping_for_Gdańsk_using_Openstreetmap'
output_dir = os.path.join(property_dir, 'output_org')
os.makedirs(output_dir, exist_ok=True)


# -----------------------------
# Get all files
# -----------------------------
apartment_files = glob.glob(os.path.join(property_dir, 'apartments_pl_*.csv'))
poi_monthly_dirs = glob.glob(os.path.join(poi_dir, 'poland-*.osm'))
fallback_poi_files = glob.glob(os.path.join(fallback_poi_dir, '**', '*.csv'), recursive=True)


# -----------------------------
# Map POI monthly data by date (e.g., "2023_09")
# -----------------------------
poi_by_date = {}
for folder in poi_monthly_dirs:
    match = re.search(r'(\d{4})-(\d{2})', folder)
    if match:
        date_key = f"{match.group(1)}_{match.group(2)}"
        poi_by_date[date_key] = folder


# -----------------------------
# Helper to load POI data for a given folder
# -----------------------------
def load_poi_data(poi_folder):
    poi_files = glob.glob(os.path.join(poi_folder, '**', '*.csv'), recursive=True)
    poi_by_city_and_type = {}

    for file in poi_files:
        base = os.path.basename(file)
        parts = base.split('_')
        if len(parts) >= 3:
            city = parts[0].lower()
            category = '_'.join(parts[1:-1])
            poi_by_city_and_type.setdefault(city, {})[category] = file

    poi_data_by_city = {}
    for city, categories in poi_by_city_and_type.items():
        poi_data_by_city[city] = {}
        for category, file_path in categories.items():
            try:
                poi_df = pd.read_csv(file_path)
                poi_df = poi_df.dropna(subset=['latitude', 'longitude'])
                poi_data_by_city[city][category] = poi_df
            except Exception as e:
                print(f"Error reading POI file {file_path}: {e}")

    return poi_data_by_city


# -----------------------------
# PROCESS EACH APARTMENT FILE
# -----------------------------
for apt_file in apartment_files:
    print(f"\n🟦 Processing {os.path.basename(apt_file)}")

    # Extract date
    match = re.search(r'(\d{4})_(\d{2})', os.path.basename(apt_file))
    if match:
        date_key = f"{match.group(1)}_{match.group(2)}"
        poi_folder = poi_by_date.get(date_key, None)
        if poi_folder:
            print(f"✅ Using POI data from {os.path.basename(poi_folder)}")
        else:
            print(f"⚠️ No matching POI data for {date_key}, using fallback Gdańsk dataset.")
            poi_folder = fallback_poi_dir
    else:
        print(f"⚠️ No date found in filename, using fallback Gdańsk dataset.")
        poi_folder = fallback_poi_dir

    # Load POI data (either dated or fallback)
    poi_data_by_city = load_poi_data(poi_folder)

    # Load apartment data
    try:
        properties = pd.read_csv(apt_file)
        properties['latitude'] = properties['latitude'].astype(float)
        properties['longitude'] = properties['longitude'].astype(float)
        properties['city'] = properties['city'].str.lower().str.strip()

        distance_data = []

        # Compute distance matrix for each property
        for idx, row in properties.iterrows():
            city = row['city']
            lat1, lon1, prop_id = row['latitude'], row['longitude'], row['id']
            distances = {'id': prop_id}

            if city in poi_data_by_city:
                for category, poi_df in poi_data_by_city[city].items():
                    try:
                        # Compute vectorized distances
                        poi_df['distance'] = haversine_vectorized(
                            lat1, lon1,
                            poi_df['latitude'].values, poi_df['longitude'].values
                        )

                        # Weighted distance for green spaces
                        if category == 'green_spaces' and 'score' in poi_df.columns:
                            poi_df['score'] = pd.to_numeric(poi_df['score'], errors='coerce').fillna(0)
                            poi_df['combined_metric'] = poi_df['distance'] / (poi_df['score'] + 1)
                            top3 = poi_df.nsmallest(3, 'combined_metric')
                        else:
                            top3 = poi_df.nsmallest(3, 'distance')

                        # Store top-3 distances and scores
                        for i, (_, poi_row) in enumerate(top3.iterrows()):
                            distances[f'distance_to_{category}_{i+1}'] = poi_row['distance']
                            if category == 'green_spaces' and 'score' in poi_row:
                                distances[f'score_of_{category}_{i+1}'] = poi_row['score']

                    except Exception as e:
                        print(f"Error processing {category} for {city}: {e}")
            else:
                print(f"No POI data for city: {city}")

            distance_data.append(distances)

        # Merge distance data and save output
        distance_df = pd.DataFrame(distance_data)
        final_df = pd.merge(properties, distance_df, on='id', how='left')

        output_file = os.path.basename(apt_file).replace('.csv', '_with_poi.csv')
        final_df.to_csv(os.path.join(output_dir, output_file), index=False)
        print(f"💾 Saved: {output_file}")

    except Exception as e:
        print(f"❌ Failed to process {apt_file}: {e}")
