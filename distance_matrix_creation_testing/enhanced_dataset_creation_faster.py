import pandas as pd
import numpy as np
from math import radians
import glob
import os
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

# Haversine vectorized
def haversine_vectorized(lat1, lon1, lat2_array, lon2_array):
    R = 6371
    dlat = np.radians(lat2_array - lat1)
    dlon = np.radians(lon2_array - lon1)
    a = np.sin(dlat / 2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2_array)) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

# Global POI data cache to be passed to each process
def load_poi_data(poi_dir):
    poi_files = glob.glob(os.path.join(poi_dir, '**', '*.csv'), recursive=True)
    poi_by_city_and_type = {}

    for file in poi_files:
        base = os.path.basename(file)
        parts = base.split('_')
        if len(parts) >= 3:
            city = parts[0].lower()
            category = '_'.join(parts[1:-1])
            poi_df = pd.read_csv(file).dropna(subset=['latitude', 'longitude'])
            poi_df['latitude'] = poi_df['latitude'].astype(float)
            poi_df['longitude'] = poi_df['longitude'].astype(float)
            if city not in poi_by_city_and_type:
                poi_by_city_and_type[city] = {}
            poi_by_city_and_type[city][category] = poi_df

    return poi_by_city_and_type

# Single file processing function
def process_apartment_file(apt_file, poi_by_city_and_type, output_dir):
    print(f"Processing {apt_file}...")
    try:
        properties = pd.read_csv(apt_file)
        properties['latitude'] = properties['latitude'].astype(float)
        properties['longitude'] = properties['longitude'].astype(float)
        properties['city'] = properties['city'].str.lower().str.strip()

        distance_data = []

        for row in properties.itertuples(index=False):
            city = row.city
            lat1 = row.latitude
            lon1 = row.longitude
            prop_id = row.id
            distances = {'id': prop_id}

            if city in poi_by_city_and_type:
                for category, poi_df in poi_by_city_and_type[city].items():
                    try:
                        distances_array = haversine_vectorized(lat1, lon1, poi_df['latitude'].values, poi_df['longitude'].values)
                        poi_df_copy = poi_df.copy()
                        poi_df_copy['distance'] = distances_array

                        if category == 'green_spaces' and 'score' in poi_df_copy.columns:
                            poi_df_copy['score'] = pd.to_numeric(poi_df_copy['score'], errors='coerce').fillna(0)
                            poi_df_copy['combined_metric'] = poi_df_copy['distance'] / (poi_df_copy['score'] + 1)
                            top3 = poi_df_copy.nsmallest(3, 'combined_metric')
                        else:
                            top3 = poi_df_copy.nsmallest(3, 'distance')

                        for i, poi_row in top3.iterrows():
                            distances[f'distance_to_{category}_{i+1}'] = poi_row['distance']
                            if category == 'green_spaces' and 'score' in poi_row:
                                distances[f'score_of_{category}_{i+1}'] = poi_row['score']
                    except Exception as e:
                        print(f"Error processing POI category {category}: {e}")
            else:
                print(f"No POI data for city: {city}")

            distance_data.append(distances)

        distance_df = pd.DataFrame(distance_data)
        final_df = pd.merge(properties, distance_df, on='id', how='left')

        output_file = os.path.basename(apt_file).replace('.csv', '_with_poi.csv')
        final_df.to_csv(os.path.join(output_dir, output_file), index=False)
        print(f"Saved: {output_file}")
    except Exception as e:
        print(f"Failed to process {apt_file}: {e}")

# Entry point
def main():
    property_dir = '/Users/filiporlikowski/Documents/inżynierka/enProject/KaggleDataset'
    poi_dir = '/Users/filiporlikowski/Documents/inżynierka/enProject/scrapping_using_Openmaps'
    output_dir = os.path.join(property_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    # Load POI data once and share
    poi_data = load_poi_data(poi_dir)

    # Apartment files
    apartment_files = glob.glob(os.path.join(property_dir, 'apartments_pl_*.csv'))

    # Prepare args for multiprocessing
    tasks = [(apt_file, poi_data, output_dir) for apt_file in apartment_files]

    # Use multiprocessing
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(process_apartment_file, *task) for task in tasks]
        for future in futures:
            future.result()  # Wait for all to complete

if __name__ == '__main__':
    main()
