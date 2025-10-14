import pandas as pd

df = pd.read_csv('/Users/filiporlikowski/Documents/EngeneeringProject/KaggleDataset/output_org/apartments_pl_2023_09_with_poi.csv')
nan_columns = df.columns[df.isna().any()]
print(len(df))
print("Columns with NaNs:\n", df[nan_columns].isna().sum())