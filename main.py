import requests  # Import the requests library to send HTTP requests

# Set the latitude and longitude of the target location (example: Warsaw)
latitude, longitude = 52.2298, 21.0122

# Overpass API URL (used to query OpenStreetMap data)
overpass_url = "http://overpass-api.de/api/interpreter"

# Overpass query to find bus stops within a 1000-meter (1 km) radius
overpass_query = f"""
[out:json];  # Output format as JSON
node["highway"="bus_stop"](around:1000,{latitude},{longitude});  # Find bus stops in the area
out;  # Output the results
"""

# Send the request to Overpass API with the query
response = requests.get(overpass_url, params={"data": overpass_query}).json()

# Extract bus stop elements from the API response
bus_stops = response.get("elements", [])

# Check if any bus stops were found
if bus_stops:
    # Get the latitude and longitude of the nearest bus stop
    stop_lat, stop_lng = bus_stops[0]["lat"], bus_stops[0]["lon"]
    print(f"Nearest bus stop at: {stop_lat}, {stop_lng}")
else:
    # If no bus stops are found, display a message
    print("No bus stops found nearby.")
