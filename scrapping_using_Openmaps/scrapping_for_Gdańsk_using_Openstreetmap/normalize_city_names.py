import os

def enhance_dataset(city):
    """Normalize city name for filename use."""
    city = city.lower().replace("ą", "a").replace("ś", "s").replace("ł", "l").replace("ń", "n") \
                       .replace("ć", "c").replace("ó", "o").replace("ż", "z").replace("ź", "z") \
                       .replace("ę", "e")
    return city.replace(" ", "_")

# List all files in the current directory
for filename in os.listdir():
    if filename.endswith(".csv"):
        city_name = filename[:-4]  # Remove ".csv"
        new_name = enhance_dataset(city_name) + ".csv"
        os.rename(filename, new_name)
        print(f"Renamed: {filename} -> {new_name}")