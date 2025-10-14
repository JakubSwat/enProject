import os
import glob
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

directory_path = '/Users/filiporlikowski/Documents/enProject/training_of_price_predictive_model/'
csv_files = glob.glob(os.path.join(directory_path, '*.csv'))

categorical_columns = ['city', 'type', 'ownership', 'buildingMaterial', 'condition']
yes_no_columns = ['hasParkingSpace', 'hasBalcony', 'hasElevator', 'hasSecurity', 'hasStorageRoom']

for csv_file in csv_files:
    df = pd.read_csv(csv_file)

    # Identify columns with >50% NaNs
    cols_to_drop = df.columns[df.isna().mean() > 0.5].tolist()
    if cols_to_drop:
        print(f"Dropping columns in {os.path.basename(csv_file)} due to >50% NaNs: {cols_to_drop}")

    # Drop those columns
    df = df.loc[:, df.isna().mean() < 0.5]

    # Fill numeric NaNs with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    # Fill categorical NaNs with 'missing'
    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].fillna('missing')

    # Map yes/no columns to 1/0
    for col in yes_no_columns:
        if col in df.columns:
            df[col] = df[col].map({'yes': 1, 'no': 0}).fillna(0)

    # Label encode categorical columns
    encoder = LabelEncoder()
    for col in categorical_columns:
        if col in df.columns:
            df[col] = encoder.fit_transform(df[col])

    # Save processed file
    df.to_csv(csv_file, index=False)
