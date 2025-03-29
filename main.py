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
latitude, longitude = 53.3789332, 14.6252957

# Overpass API URL (used to query OpenStreetMap data)
overpass_url = "http://overpass-api.de/api/interpreter"

# Overpass query to find bus stops within a 1000-meter (1 km) radius
overpass_query = f"""
[out:json];
(
  node["highway"="bus_stop"](around:500,{latitude},{longitude});
);
out body;
"""

# Send the request to Overpass API with the query
response = requests.get(overpass_url, params={"data": overpass_query}).json()

# Extract bus stop elements from the API response
bus_stops = response.get("elements", [])

# Check if any bus stops were found
if bus_stops:
    # Get the latitude and longitude of the nearest bus stop
    stop_lat, stop_lng = bus_stops[0]["lat"], bus_stops[0]["lon"]
    dist = distance(latitude,longitude, stop_lat, stop_lng)
    coordinates = [stop_lat, stop_lng]
    for stop in bus_stops:  # `stop` is already a dictionary
        stop_lat2, stop_lng2 = stop["lat"], stop["lon"]
        if dist > distance(latitude, longitude, stop_lat2, stop_lng2):
            dist = distance(latitude, longitude, stop_lat2, stop_lng2)
            coordinates = [stop_lat2, stop_lng2]
    print(f"Nearest bus stop at: {coordinates[0]}, {coordinates[1]} \ndistance to location: {dist}")
else:
    # If no bus stops are found, display a message
    print("No bus stops found nearby.")
