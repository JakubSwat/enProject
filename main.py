import requests  # Import the requests library to send HTTP requests
from math import radians, sin, cos, sqrt, atan2 #computes the central angle (in radians)
                                                    # between two points on a sphere.

def distance(latBase, longBase, lat2, long2):   #calculates the distance on a map from
                                                    # base coordinated to found pint of interest
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [latBase, longBase, lat2, long2])  # Convert to radians
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Set the latitude and longitude of the target location (example: Warsaw)
latitude, longitude = 54.360016, 18.647321

#radius of scouting for places
radius = 1000

# Overpass API URL (used to query OpenStreetMap data)
overpass_url = "http://overpass-api.de/api/interpreter"


def find_nearest(query):
    overpass_query = f"""
    [out:json];
    (
      {query}(around:{radius},{latitude},{longitude});
    );
    out body;
    """
    # Send the request to Overpass API with the query
    response = requests.get(overpass_url, params={"data": overpass_query}).json()

    # Extract point of interest elements from the API response
    elements = response.get("elements", [])

    if elements: # Check if any results were found
        # Find the closest element using the minimum distance function
        nearest = min(elements, key=lambda e: distance(latitude,longitude, e["lat"], e["lon"]))
        return nearest["lat"], nearest["lon"], distance(latitude,longitude, nearest["lat"], nearest["lon"])
    return None # Return None if no elements are found

categories = {
    "Bus Stop": 'node["highway"="bus_stop"]',  # Bus stops
    "Park": 'node["leisure"="park"]',  # Parks
    "Shop": 'node["shop"]',  # Shops and retail areas
    "Museum": 'node["tourism"="museum"]',  # Museums
}

results = {}
for category, query in categories.items():
    result = find_nearest(query)
    if result:
        results[category] = result

for category, (lat, lon, dist) in results.items():
    print(f"Nearest {category} at {lat}, {lon}, Distance: {dist} km")



