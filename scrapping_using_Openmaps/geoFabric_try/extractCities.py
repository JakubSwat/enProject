import subprocess
import os

# pełna ścieżka do pliku PBF
PBF_POLAND = "/home/jakubswat/PycharmProjects/enProject/scrapping_using_Openmaps/geoFabric_try/geofabrik_pbf_files/poland-latest.osm.pbf"

# katalog wyjściowy
OUTPUT_DIR = "/home/jakubswat/PycharmProjects/enProject/scrapping_using_Openmaps/geoFabric_try/extracted_cities"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# przykładowe miasto
city_name = "Gdansk"
bbox = [18.541, 54.279, 18.731, 54.469]
output_file = os.path.join(OUTPUT_DIR, f"{city_name.lower()}.osm.pbf")

# wycinanie miasta
subprocess.run([
    "osmium", "extract",
    "-b", ",".join(map(str, bbox)),
    PBF_POLAND,
    "-o", output_file,
    "--overwrite"
], check=True)

print(f"Wycięto {city_name} -> {output_file}")
