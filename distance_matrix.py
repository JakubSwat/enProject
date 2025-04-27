import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import argparse

# Function to calculate Haversine distance between two points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c

def calculate_distance_matrix(file1_path, file2_path):
    # Load both CSVs
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)

    # Initialize empty DataFrame to store distances
    distance_matrix = pd.DataFrame(index=df1['name'], columns=df2['name'])

    # Loop through each point in df1 and df2
    for idx1, row1 in df1.iterrows():
        for idx2, row2 in df2.iterrows():
            dist = haversine(row1['latitude'], row1['longitude'], row2['latitude'], row2['longitude'])
            distance_matrix.loc[row1['name'], row2['name']] = dist

    return distance_matrix

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate distance matrix between two location files.")
    parser.add_argument("file1", help="Path to the first CSV file (source locations)")
    parser.add_argument("file2", help="Path to the second CSV file (target locations)")

    args = parser.parse_args()

    # Run the function
    matrix = calculate_distance_matrix(args.file1, args.file2)

    # Show results
    print(matrix)

    # Optional: save to CSV
    matrix.to_csv('distance_matrix.csv')
#Przykład Jak odpalić
#python distance_matrix.py /Users/filiporlikowski/Documents/inżynierka/enProject/bus_stops_locations.csv /Users/filiporlikowski/Documents/inżynierka/enProject/entertainment_places_locations.csv

