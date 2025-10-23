# --- Imports (keep your existing imports) ---
import json
from collections import defaultdict

# --- BEFORE building heat_data: log + percentile clipping + robust city names ---
# log-transform prices for better spread
df['price_per_sqm_log'] = np.log1p(df['price_per_sqm'])

# percentile clipping to remove extreme tail influence
p_low = df['price_per_sqm_log'].quantile(0.05)
p_high = df['price_per_sqm_log'].quantile(0.95)
df['price_clipped'] = df['price_per_sqm_log'].clip(lower=p_low, upper=p_high)

# normalized 0..1 (global)
df['price_norm_global'] = (df['price_clipped'] - p_low) / (p_high - p_low)

# safe city column
if 'city' in df.columns:
    df['city_clean'] = df['city'].astype(str).str.strip().str.lower()
else:
    df['city_clean'] = ""

# --- Aggregate per month + spatial binning to reduce point count ---
df['year_month'] = df['date'].dt.to_period('M')
time_index = sorted(df['year_month'].unique())
print(f"Will build heat frames for {len(time_index)} timesteps.")

def aggregate_frame(subset, round_digits=4):
    """
    Aggregate subset by rounding lat/lon to `round_digits`. Return list of [lat, lon, weight].
    Weight = mean(price_norm_global) per bin.
    """
    if subset.empty:
        return []
    # round coords to create bins (adjust round_digits to control granularity)
    subset['lat_r'] = subset['latitude'].round(round_digits)
    subset['lon_r'] = subset['longitude'].round(round_digits)
    # group by bin and compute mean intensity and count
    agg = subset.groupby(['lat_r','lon_r'])['price_norm_global'].agg(['mean','count']).reset_index()
    # optional: drop bins with tiny counts to reduce noise
    agg = agg[agg['count'] >= 1]  # tune threshold
    # build list [lat, lon, intensity], clip intensity to <=0.95 to avoid saturation
    agg['mean_clip'] = agg['mean'].clip(upper=0.95)
    return agg[['lat_r','lon_r','mean_clip']].values.tolist()

heat_data_global = []
heat_data_city = []

for period in time_index:
    subset = df[df['year_month'] == period].copy()
    print(f"\nMonth {period}: total points = {len(subset)}")

    # build global aggregated frame
    global_frame = aggregate_frame(subset, round_digits=4)
    print(f"  aggregated global bins: {len(global_frame)}")
    heat_data_global.append(global_frame)

    # build city aggregated frame for local city
    if 'city' in df.columns and CITY_FOR_LOCAL_HEATMAP:
        city_subset = subset[subset['city_clean'] == CITY_FOR_LOCAL_HEATMAP.lower()].copy()
        print(f"  {CITY_FOR_LOCAL_HEATMAP} points this month: {len(city_subset)}")
        if not city_subset.empty:
            # For local intensity, do local log+clip then normalize per city to enhance local contrast
            city_subset['price_log'] = np.log1p(city_subset['price_per_sqm'])
            c_low = city_subset['price_log'].quantile(0.05)
            c_high = city_subset['price_log'].quantile(0.95)
            city_subset['price_clipped_local'] = city_subset['price_log'].clip(c_low, c_high)
            city_subset['price_norm_local'] = (city_subset['price_clipped_local'] - c_low) / (c_high - c_low) if c_high>c_low else 0.5
            # use price_norm_local as weight when aggregating (temporarily replace price_norm_global)
            city_frame = city_subset.copy()
            city_frame['price_norm_global'] = city_frame['price_norm_local']
            local_agg = aggregate_frame(city_frame, round_digits=4)
            print(f"  aggregated city bins: {len(local_agg)}")
            heat_data_city.append(local_agg)
        else:
            heat_data_city.append([])
    else:
        heat_data_city.append([])

# --- HeatMapWithTime: tuned params (smaller radius, slightly higher blur optional) ---
HeatMapWithTime(
    data=heat_data_global,
    index=[str(x) for x in time_index],
    auto_play=False,
    max_opacity=0.6,
    radius=10,        # adjust: bigger for coarser bins, smaller for finer
    blur=12,
    scale_radius=False,
    use_local_extrema=True,   # scale per timestep to reveal monthly differences
).add_to(m)

# Local city heatmap layer (as FeatureGroup)
fg_city = folium.FeatureGroup(name=f"{CITY_FOR_LOCAL_HEATMAP.capitalize()} local heatmap")
HeatMapWithTime(
    data=heat_data_city,
    index=[str(x) for x in time_index],
    auto_play=False,
    max_opacity=0.7,
    radius=8,
    blur=10,
    scale_radius=False,
    use_local_extrema=True
).add_to(fg_city)
fg_city.add_to(m)

# --- Read districts geojson without Fiona (avoid fiona.path issue) ---
if DISTRICTS_GEOJSON:
    try:
        with open(DISTRICTS_GEOJSON, 'r', encoding='utf-8') as f:
            gj = json.load(f)
        gdf = gpd.GeoDataFrame.from_features(gj['features'])
        print("Loaded districts GeoJSON with columns:", list(gdf.columns))
        # check/rename district column to 'district' if necessary
        # e.g., if gdf contains 'nazwa' or 'name' use that
        if 'district' not in gdf.columns:
            # try common alternatives
            for alt in ('name','nazwa','nazwa_dziel','dzielnica'):
                if alt in gdf.columns:
                    gdf = gdf.rename(columns={alt: 'district'})
                    print(f"  Renamed GeoJSON column '{alt}' -> 'district'")
                    break
        # merge if district column present
        if 'district' in df.columns and 'district' in gdf.columns:
            avg_price = df.groupby('district')['price_per_sqm'].mean().reset_index()
            gdf = gdf.merge(avg_price, on='district', how='left')
            Choropleth(geo_data=gdf,
                       data=gdf,
                       columns=['district','price_per_sqm'],
                       key_on='feature.properties.district',
                       fill_color='YlOrRd',
                       fill_opacity=0.6,
                       line_opacity=0.2,
                       legend_name='Avg price/m²').add_to(m)
        else:
            print("  Skipping district choropleth (missing 'district' column in DF or GeoJSON).")
    except Exception as e:
        print("⚠️ District overlay failed (fallback). Error:", e)
