import pandas as pd


def downsample_csv(input_csv, output_csv, factor=200):
    # Read the input CSV file into a DataFrame
    df = pd.read_csv(input_csv)

    # Downsample by taking every 'factor' row
    df_downsampled = df.iloc[::factor].reset_index(drop=True)

    # Save the downsampled DataFrame to a new CSV file
    df_downsampled.to_csv(output_csv, index=False)
    print(f"✅ Saved downsampled file to {output_csv}")

downsample_csv('apartments_pl_2023_08.csv', 'apartments_pl_2023_08_smaller.csv')