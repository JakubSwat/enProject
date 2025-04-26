import os
import geopandas as gpd

from scrapping.scrapping_for_Gdańsk_using_Openstreetmap.ultimate_scrapping_tool_divided.scrapping_shopping_locations import \
    before_drop

# Directory where all shapefiles are
shapefiles_dir = "/Users/filiporlikowski/Documents/inżynierka/enProject/scrapping_using_Geofabrik_file_and_downloaded_city_shapefiles/pomorskie-latest-free"

# Gdańsk polygon file
polygon_path = "/Users/filiporlikowski/Documents/inżynierka/enProject/scrapping_using_Geofabrik_file_and_downloaded_city_shapefiles/shapefiles/Gdańsk.geojson"  # <-- your file

# Feature you want to search for
fclass_filter = "kindergarten"

# Output folder
output_dir = "/Users/filiporlikowski/Documents/inżynierka/enProject/scrapping_using_Geofabrik_file_and_downloaded_city_shapefiles/extracted_data"
os.makedirs(output_dir, exist_ok=True)

# Load Gdańsk polygon
gdansk_gdf = gpd.read_file(polygon_path)

# Make sure it’s a single (merged) polygon
if gdansk_gdf.geometry.iloc[0].geom_type == 'MultiPolygon':
    gdansk_polygon = gdansk_gdf.geometry.iloc[0].convex_hull
else:
    gdansk_polygon = gdansk_gdf.geometry.iloc[0]

# Iterate over shapefiles
for filename in os.listdir(shapefiles_dir):
    if filename.endswith(".shp"):
        filepath = os.path.join(shapefiles_dir, filename)
        print(f"Processing {filename}...")

        try:
            gdf = gpd.read_file(filepath)

            # Check if 'fclass' exists
            if 'fclass' not in gdf.columns:
                print(f"Skipping {filename}: no 'fclass' field.")
                continue

            # Filter by fclass
            filtered = gdf[gdf['fclass'] == fclass_filter]

            if filtered.empty:
                print(f"No {fclass_filter} found in {filename}.")
                continue

            # Drop missing geometry
            before_drop = len(filtered)
            filtered = filtered.dropna(subset=['geometry'])
            after_drop = len(filtered)
            print(f'Dropped {before_drop - after_drop} with missing geometry.')

            # Keep only points within Gdańsk polygon
            filtered = filtered[filtered.within(gdansk_polygon)]

            # Prepare columns
            filtered['name'] = filtered['name'].str.strip() if 'name' in filtered.columns else ""
            filtered['lon'] = filtered.geometry.x
            filtered['lat'] = filtered.geometry.y

            # Drop duplicates
            before_drop = len(filtered)
            filtered = filtered.drop_duplicates(subset=['name', 'lon', 'lat']).reset_index(drop=True)
            after_drop = len(filtered)
            print(f'Dropped {before_drop - after_drop} with duplicate name and geometry.')

            if not filtered.empty:
                output_csv = os.path.join(output_dir, f"{filename.replace('.shp', '')}_{fclass_filter}.csv")
                filtered[['name', 'lat', 'lon']].to_csv(output_csv, index=False)
                print(f"Saved {len(filtered)} records to {output_csv}")
            else:
                print(f"No {fclass_filter} found inside Gdańsk polygon in {filename}.")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

print("Done.")
