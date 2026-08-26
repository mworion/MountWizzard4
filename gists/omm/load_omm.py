import json
from skyfield.api import load, EarthSatellite

# 1. Initialize timescale generator
ts = load.timescale()

# 2. Read and fix the stream format into valid JSON
filepath = 'test.omm'

with open(filepath, 'r') as f:
    omm_records = json.load(f)  # Validate JSON format

# 3. Parse each OMM record into a Skyfield EarthSatellite object
satellites = [EarthSatellite.from_omm(ts, record) for record in omm_records]

# --- Verification & Inspection ---
print(f"Successfully loaded {len(satellites)} satellites:\n")

for sat in satellites:
    print(f"Name:     {sat.name}")
    print(f"NORAD ID: {sat.model.satnum}")
    print(f"Epoch:    {sat.epoch.utc_iso()}")
    print("-" * 35)