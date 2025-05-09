import pandas as pd
import numpy as np


# Define a function to calculate the Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c  # Distance in km


# Example DataFrame (you can load your actual dataset here)
data = [
    {"id": "f8524536d4b09a0c8ccc0197ec9d7bde", "city": "szczecin", "type": "blockOfFlats", "latitude": 53.3789332,
     "longitude": 14.6252957},
    {"id": "a8efd3561b9767b6a8cd4438bcc8a568", "city": "szczecin", "type": "tenement", "latitude": 53.3789332,
     "longitude": 14.6252957},
    {"id": "3b338e2f55c7b0f70ccc4941d9e196b9", "city": "szczecin", "type": "blockOfFlats", "latitude": 53.3765,
     "longitude": 14.6603},
    # Add the rest of the data
]

df = pd.DataFrame(data)

# Create a new column to store distances to the top 3 closest properties
df['top_3_closest'] = df.apply(lambda row: find_top_3_closest(row, df), axis=1)


def find_top_3_closest(row, df):
    # Filter by the same city and type
    city_filtered = df[(df['city'] == row['city']) & (df['type'] == row['type']) & (df['id'] != row['id'])]

    # Calculate the distances to each other property in the same city and type
    city_filtered['distance'] = city_filtered.apply(
        lambda x: haversine(row['latitude'], row['longitude'], x['latitude'], x['longitude']), axis=1)

    # Sort by distance and select the top 3 closest
    closest = city_filtered.sort_values('distance').head(3)

    # Return the ids and distances of the top 3 closest properties
    return closest[['id', 'distance']].to_dict(orient='records')


# Example of printing the enhanced data
print(df[['id', 'top_3_closest']])
