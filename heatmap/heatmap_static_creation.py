"""
heatmap_static.py
Generates a static (no time slider) heatmap of property prices in Poland.
Supports optional district shapes (GeoJSON or shapefiles).
"""

import os
import json
import numpy as np
import pandas as pd
import folium
from folium.plugins import HeatMap

import geopandas as gpd  # only needed if using shapefiles

# -------------------------
# USER CONFIG
# -------------------------
CSV_PATH = "merged_dataset_with_org_cat_values.csv"
# Optional: add district boundaries
SHAPE_PATH = None               # e.g. "districts.geojson"
SHAPE_SHP_PATH = None           # e.g. "shapefiles/districts.shp"

OUT_HTML = "poland_price_heatmap_static.html"

# Column names
LAT_COL = "latitude"
LON_COL = "longitude"
PRICE_COL = "price"

# Heatmap styling
RADIUS = 12
BLUR = 15
MAX_OPACITY = 0.8

# Poland center
MAP_CENTER = [52.237049, 21.017532]   # Warsaw
MAP_ZOOM_START = 6


# -------------------------
# Helpers
# -------------------------
def load_data(csv_path):
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=[LAT_COL, LON_COL, PRICE_COL])
    return df


def normalize_weights(series):
    """Use log1p for price, then scale 0–1."""
    s = np.log1p(series.astype(float))
    if s.max() > s.min():
        return (s - s.min()) / (s.max() - s.min())
    else:
        return s * 0.0


def add_geojson_layer(folium_map, geojson_path, layer_name="Districts", style_kw=None):
    """Overlay a GeoJSON boundary layer."""
    with open(geojson_path, "r", encoding="utf-8") as f:
        gj = json.load(f)

    def style_function(feature):
        base = {
            "fillColor": "#ffffff",
            "color": "#000000",
            "weight": 1,
            "fillOpacity": 0.0,
        }
        if style_kw:
            base.update(style_kw)
        return base

    folium.GeoJson(gj, name=layer_name, style_function=style_function).add_to(folium_map)


# -------------------------
# Main generator
# -------------------------
def main():
    print("Loading data...")
    df = load_data(CSV_PATH)

    # Keep only points in Poland approximate bbox
    df = df[
        df[LON_COL].between(14.0, 24.5) &
        df[LAT_COL].between(48.5, 55.0)
    ]

    print(f"Using {len(df)} points inside Poland bbox")

    # Normalize weights
    weights = normalize_weights(df[PRICE_COL])

    # Prepare list of points [lat, lon, weight]
    heat_data = [
        [float(lat), float(lon), float(w)]
        for lat, lon, w in zip(df[LAT_COL], df[LON_COL], weights)
    ]

    # Create map
    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM_START,
        tiles="CartoDB positron"
    )

    # Add heatmap layer
    HeatMap(
        heat_data,
        radius=RADIUS,
        blur=BLUR,
        max_opacity=MAX_OPACITY,
        name="Price Heatmap"
    ).add_to(m)

    # Add optional boundaries
    if SHAPE_SHP_PATH and os.path.exists(SHAPE_SHP_PATH):
        print("Converting shapefile to GeoJSON...")
        gdf = gpd.read_file(SHAPE_SHP_PATH)
        tmp = "temp_boundaries.geojson"
        gdf.to_file(tmp, driver="GeoJSON")
        add_geojson_layer(m, tmp, layer_name="Districts", style_kw={"color": "#333333"})
    elif SHAPE_PATH and os.path.exists(SHAPE_PATH):
        print("Adding GeoJSON boundaries...")
        add_geojson_layer(m, SHAPE_PATH, layer_name="Districts", style_kw={"color": "#333333"})
    else:
        print("No district shapes added.")

    folium.LayerControl().add_to(m)

    print(f"Saving HTML → {OUT_HTML}")
    m.save(OUT_HTML)
    print("Done.")


# -------------------------
if __name__ == "__main__":
    main()
