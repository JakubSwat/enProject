import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import glob
import os

# Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Directories
property_dir = '/Users/filiporlikowski/Documents/inżynierka/enProject/KaggleDataset'
poi_dir = '/Users/filiporlikowski/Documents/inżynierka/enProject/scrapping_using_Openmaps'
output_dir = os.path.join(property_dir, 'output')
os.makedirs(output_dir, exist_ok=True)

# Load all POI files
poi_files = glob.glob(os.path.join(poi_dir, '**', '*.csv'), recursive=True)

# Organize POI files: {city: {category: file}}
poi_by_city_and_type = {}
for file in poi_files:
    base = os.path.basename(file)
    parts = base.split('_')
    if len(parts) >= 3:
        city = parts[0].lower()
        category = '_'.join(parts[1:-1])  # removes "_locations.csv"
        if city not in poi_by_city_and_type:
            poi_by_city_and_type[city] = {}
        poi_by_city_and_type[city][category] = file

# Process each apartment file
apartment_files = glob.glob(os.path.join(property_dir, 'apartments_pl_*.csv'))

for apt_file in apartment_files:
    print(f"Processing {apt_file}...")
    try:
        properties = pd.read_csv(apt_file)
        properties['latitude'] = properties['latitude'].astype(float)
        properties['longitude'] = properties['longitude'].astype(float)
        properties['city'] = properties['city'].str.lower().str.strip()

        distance_data = []

        for idx, row in properties.iterrows():
            city = row['city']
            lat1 = row['latitude']
            lon1 = row['longitude']
            prop_id = row['id']
            distances = {'id': prop_id}

            if city in poi_by_city_and_type:
                for category, filepath in poi_by_city_and_type[city].items():
                    try:
                        poi_df = pd.read_csv(filepath)
                        poi_df = poi_df.dropna(subset=['latitude', 'longitude'])

                        # Calculate distance to each POI
                        poi_df['distance'] = poi_df.apply(
                            lambda x: haversine(lat1, lon1, float(x['latitude']), float(x['longitude'])), axis=1
                        )

                        # Score-weighted top 3 for green spaces
                        if category == 'green_spaces' and 'score' in poi_df.columns:
                            poi_df['score'] = pd.to_numeric(poi_df['score'], errors='coerce').fillna(0)
                            poi_df['combined_metric'] = poi_df['distance'] / (poi_df['score'] + 1)
                            top3 = poi_df.nsmallest(3, 'combined_metric')
                        else:
                            top3 = poi_df.nsmallest(3, 'distance')

                        # Save distances (and scores)
                        for i, (_, poi_row) in enumerate(top3.iterrows()):
                            distances[f'distance_to_{category}_{i+1}'] = poi_row['distance']
                            if category == 'green_spaces' and 'score' in poi_row:
                                distances[f'score_of_{category}_{i+1}'] = poi_row['score']
                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")
            else:
                print(f"No POI files for city: {city}")

            distance_data.append(distances)

        distance_df = pd.DataFrame(distance_data)
        final_df = pd.merge(properties, distance_df, on='id', how='left')

        output_file = os.path.basename(apt_file).replace('.csv', '_with_poi.csv')
        final_df.to_csv(os.path.join(output_dir, output_file), index=False)
        print(f"Saved: {output_file}")

    except Exception as e:
        print(f"Failed to process {apt_file}: {e}")
