import pandas as pd

df = pd.read_csv('/Users/filiporlikowski/Documents/enProject/training_of_price_predictive_model/merged_dataset.csv')
nan_columns = df.columns[df.isna().any()]
print(len(df))
print("Columns with NaNs:\n", df[nan_columns].isna().sum())