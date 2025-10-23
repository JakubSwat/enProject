import pandas as pd
import glob
import os

# Path to your KaggleDataset folder
folder_path = "/Users/filiporlikowski/Documents/EngeneeringProject/KaggleDataset"

# Get all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

# Set to collect unique city names
unique_cities = set()

# Loop through each file and extract cities
for file in csv_files:
    try:
        df = pd.read_csv(file, usecols=['city'])
        unique_cities.update(df['city'].dropna().unique())
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Print results
print(f"Number of unique cities: {len(unique_cities)}")
# Optional: print or save the cities
print("Cities:", sorted(unique_cities))


