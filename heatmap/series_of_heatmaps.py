import os
import json
import numpy as np
import pandas as pd
import folium
from folium.plugins import HeatMap

from datetime import datetime

# -----------------------------
# CONFIGURATION
# -----------------------------
CSV_PATH = "merged_dataset_with_org_cat_values.csv"
OUTPUT_DIR = "heatmaps"
OUTPUT_INDEX = "index.html"

LAT_COL = "latitude"
LON_COL = "longitude"
PRICE_COL = "price"
DATE_COL = "date"

# Aggregation level:
# "day", "week", or "month"
DATE_MODE = "day"          # choose: "day" / "week" / "month"

# Poland center
MAP_CENTER = [52.237049, 21.017532]
MAP_ZOOM = 6


def normalize_weights(series):
    s = np.log1p(series.astype(float))
    if s.max() > s.min():
        return (s - s.min()) / (s.max() - s.min())
    return s * 0.0


def load_and_group_data():
    df = pd.read_csv(CSV_PATH, parse_dates=[DATE_COL])
    df = df.dropna(subset=[LAT_COL, LON_COL, PRICE_COL])

    df = df[
        df[LON_COL].between(14.0, 24.5) &
        df[LAT_COL].between(48.5, 55.0)
    ]

    if DATE_MODE == "day":
        df["period"] = df[DATE_COL].dt.strftime("%Y-%m-%d")
    elif DATE_MODE == "week":
        df["period"] = df[DATE_COL].dt.to_period("W").astype(str)
    elif DATE_MODE == "month":
        df["period"] = df[DATE_COL].dt.to_period("M").astype(str)
    else:
        raise ValueError("DATE_MODE must be 'day', 'week', or 'month'")

    return df


def generate_heatmap(df, period, out_file):
    subset = df[df["period"] == period]
    if subset.empty:
        return False

    weights = normalize_weights(subset[PRICE_COL])

    heat_data = [
        [float(lat), float(lon), float(w)]
        for lat, lon, w in zip(subset[LAT_COL], subset[LON_COL], weights)
    ]

    m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="CartoDB positron")

    HeatMap(
        heat_data,
        radius=12,
        blur=15,
        max_opacity=0.8,
        name=f"Heatmap {period}"
    ).add_to(m)

    m.save(out_file)
    return True


def generate_index_page(periods):
    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Heatmap Viewer</title>
<style>
body {
    font-family: Arial, sans-serif;
    margin: 20px;
}
iframe {
    width: 100%;
    height: 90vh;
    border: 1px solid #aaa;
}
.controls {
    margin-bottom: 10px;
}
button {
    padding: 8px 14px;
    margin-right: 10px;
    font-size: 14px;
}
select {
    padding: 6px;
    font-size: 14px;
}
</style>
</head>
<body>

<h2>Heatmap Viewer</h2>

<div class="controls">
    <button onclick="prev()">Previous</button>
    <button onclick="next()">Next</button>

    <select id="periodSelect" onchange="changePeriod()">
"""

    for p in periods:
        html += f'<option value="{p}">{p}</option>\n'

    html += """
    </select>
</div>

<iframe id="viewer" src=""></iframe>

<script>
var periods = ["""

    html += ",".join([f'"{p}"' for p in periods])

    html += """];
var current = 0;

function load() {
    document.getElementById("viewer").src = "heatmaps/heatmap_" + periods[current] + ".html";
    document.getElementById("periodSelect").value = periods[current];
}

function next() {
    if (current < periods.length - 1) {
        current++;
        load();
    }
}

function prev() {
    if (current > 0) {
        current--;
        load();
    }
}

function changePeriod() {
    var sel = document.getElementById("periodSelect").value;
    current = periods.indexOf(sel);
    load();
}

window.onload = load;
</script>

</body>
</html>
"""

    with open(OUTPUT_INDEX, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    df = load_and_group_data()
    periods = sorted(df["period"].unique())

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Generating heatmaps for {len(periods)} periods...")

    for period in periods:
        out_file = f"{OUTPUT_DIR}/heatmap_{period}.html"
        print(" →", out_file)
        generate_heatmap(df, period, out_file)

    print("Building index.html...")
    generate_index_page(periods)

    print("Done! Open index.html to view the navigation interface.")


if __name__ == "__main__":
    main()
