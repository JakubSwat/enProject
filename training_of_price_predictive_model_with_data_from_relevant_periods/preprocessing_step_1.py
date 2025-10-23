import pandas as pd
import os
import re
from datetime import datetime


def load_csv_with_date(file_path: str) -> pd.DataFrame:
    """
    Loads a CSV file, extracts a date from the filename, adds a `date` column, and returns the DataFrame.
    Expected filename format: 'apartments_pl_YYYY_MM.csv'
    """
    # Extract filename
    filename = os.path.basename(file_path)

    # Extract year and month using regex
    match = re.search(r"apartments_pl_(\d{4})_(\d{2})_with_poi", filename)
    if not match:
        raise ValueError(f"Filename {filename} doesn't match expected pattern 'apartments_pl_YYYY_MM.csv'")

    year, month = match.groups()
    file_date = datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d").date()

    # Load CSV with empty values treated as NaN
    df = pd.read_csv(file_path, na_values=["", " "])

    # Add the date column
    df["date"] = file_date

    return df

data_dir = "/Users/filiporlikowski/Documents/EngeneeringProject/KaggleDataset/output_org"
all_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

dfs = []

print(all_files)
for f in all_files:
    full_path = os.path.join(data_dir, f)
    df = load_csv_with_date(full_path)
    dfs.append(df)

# Combine all into one DataFrame
merged_df = pd.concat(dfs, ignore_index=True)
merged_df.to_csv('merged_dataset_with_org_cat_values.csv', index=False)