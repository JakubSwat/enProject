import os
import requests
from tqdm import tqdm
import subprocess

# Lista dat historycznych w formacie YYMMDD
dates = [
    "230807",
    "230904"#,
    # "231002", "231106", "231204",
    # "240101", "240205", "240304", "240401", "240506", "240603"
]

# Katalog docelowy
base_dir = "./geofabrik_pbf_files"
os.makedirs(base_dir, exist_ok=True)

# URL bazowy
base_url = "https://planet.openstreetmap.org/pbf/full-history/history-{}.osm.pbf"

# Bounding box Polski: (minlon, minlat, maxlon, maxlat)
bbox_poland = (14.12, 49.00, 24.15, 54.84)

# Przykładowy zakres dat dla snapshotu
snapshot_ranges = {
    "2023-08": ("2023-07-01T00:00:00Z", "2023-07-31T23:59:59Z"),
    "2023-09": ("2023-08-01T00:00:00Z", "2023-08-31T23:59:59Z"),
    # możesz dodać kolejne miesiące
}

def download_file(url, dest_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))

        with open(dest_path, 'wb') as f, tqdm(
            total=total_size, unit='B', unit_scale=True, desc=os.path.basename(dest_path)
        ) as pbar:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        print(f"Plik zapisany: {dest_path}")
        return True
    except requests.RequestException as e:
        print(f"Błąd pobierania {url}: {e}")
        return False

def extract_poland(global_file, output_file):
    """Wycinanie Polski z pliku historycznego"""
    try:
        subprocess.run([
            "osmium", "extract", "-b",
            ",".join(map(str, bbox_poland)),
            global_file, "-o", output_file, "--with-history", "--overwrite"
        ], check=True)
        print(f"Wycięto Polskę: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Błąd przy wycinaniu Polski: {e}")

def create_snapshot(poland_file, snapshot_file, start_time, end_time):
    """Wycinanie danych z konkretnego okresu (snapshot)"""
    try:
        subprocess.run([
            "osmium", "time-filter", poland_file,
            f"{start_time},{end_time}",
            "-o", snapshot_file
        ], check=True)
        print(f"Utworzono snapshot: {snapshot_file}")
    except subprocess.CalledProcessError as e:
        print(f"Błąd przy tworzeniu snapshotu: {e}")

# Główna pętla
for date in dates:
    url = base_url.format(date)
    global_file = os.path.join(base_dir, f"history-{date}.osm.pbf")
    poland_file = os.path.join(base_dir, f"poland-{date}.osm.pbf")

    # 1. Pobieranie
    if download_file(url, global_file):
        # 2. Wycinanie Polski
        extract_poland(global_file, poland_file)

        # 3. Tworzenie snapshotów dla każdego miesiąca
        for month, (start, end) in snapshot_ranges.items():
            snapshot_file = os.path.join(base_dir, f"poland-{month}.osm.pbf")
            create_snapshot(poland_file, snapshot_file, start, end)

        # 4. Usuwanie pełnego pliku globalnego, jeśli chcesz
        # os.remove(global_file)
        # print(f"Usunięto plik globalny: {global_file}")
