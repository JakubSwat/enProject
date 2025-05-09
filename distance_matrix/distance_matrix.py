import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import argparse


# Function to calculate Haversine distance between two points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def get_top_closest_locations(df, reference_lat, reference_lon, top_n=3):
    # Calculate distance from reference point
    df['distance'] = df.apply(lambda row: haversine(reference_lat, reference_lon, row['latitude'], row['longitude']),
                              axis=1)

    # Sort by distance and get the top N closest locations
    closest_locations = df.nsmallest(top_n, 'distance')

    return closest_locations


def calculate_distance_matrix(df1, df2):
    # Initialize empty DataFrame to store distances
    distance_matrix = pd.DataFrame(index=df1['name'], columns=df2['name'])

    # Loop through each point in df1 and df2
    for idx1, row1 in df1.iterrows():
        for idx2, row2 in df2.iterrows():
            dist = haversine(row1['latitude'], row1['longitude'], row2['latitude'], row2['longitude'])
            distance_matrix.loc[row1['name'], row2['name']] = dist

    return distance_matrix


def process_data(file_paths, reference_lat, reference_lon, top_n=3):
    # Read all CSV files into a list of DataFrames
    data_frames = [pd.read_csv(file) for file in file_paths]

    # Concatenate all DataFrames into one
    full_data = pd.concat(data_frames, ignore_index=True)

    # Get the top N closest locations to the reference point
    closest_locations = get_top_closest_locations(full_data, reference_lat, reference_lon, top_n)

    return closest_locations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate distance matrix between two location files.")
    parser.add_argument("file_paths", nargs='+', help="Paths to CSV files containing locations")
    parser.add_argument("reference_lat", type=float, help="Latitude of the reference point")
    parser.add_argument("reference_lon", type=float, help="Longitude of the reference point")
    parser.add_argument("output_file", help="Path to save the output distance matrix")

    args = parser.parse_args()

    # Process data
    closest_locations = process_data(args.file_paths, args.reference_lat, args.reference_lon)

    # Optional: you can choose to print the top closest locations
    print(closest_locations)

    # If you have a second set of locations (e.g., property listings), use the same approach to load and filter them.
    # Calculate the distance matrix between closest locations and properties
    # For demonstration, we'll use the same dataset for both
    distance_matrix = calculate_distance_matrix(closest_locations, closest_locations)

    # Show results
    print(distance_matrix)

    # Save to CSV
    distance_matrix.to_csv(args.output_file)