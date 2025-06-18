import os
import glob
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Directory where the CSV files are stored
directory_path = '/Users/filiporlikowski/Documents/enProject/KaggleDataset/output_org/'

# Get all CSV files in the directory
csv_files = glob.glob(os.path.join(directory_path, '*.csv'))

# Process each CSV file
for csv_file in csv_files:
    # Load the dfset
    df = pd.read_csv(csv_file)

    # Drop columns not needed or not useful
    df.drop(columns=["id"], inplace=True)

    df = df.apply(lambda x: x.fillna(x.median()) if x.dtype != 'object' else x)

    # Step 2: Encode 'yes'/'no' columns to 1/0
    yes_no_columns = ['hasParkingSpace', 'hasBalcony', 'hasElevator', 'hasSecurity',
                      'hasStorageRoom']  # List your 'yes'/'no' columns here
    for col in yes_no_columns:
        df[col] = df[col].map({'yes': 1, 'no': 0})

    # Step 3: Convert categorical columns like 'city' and 'type' to numerical values
    # For categorical columns, we can use Label Encoding or OneHotEncoding.
    # Here, I will use Label Encoding for simplicity.
    categorical_columns = ['city', 'type', 'ownership', 'buildingMaterial',
                           'condition']  # List other categorical columns if needed
    encoder = LabelEncoder()

    for col in categorical_columns:
        df[col] = encoder.fit_transform(df[col])

    # Save the processed df to overwrite the original file
    df.to_csv(csv_file, index=False)

print("Processing complete. The original files have been overwritten with the processed df.")
