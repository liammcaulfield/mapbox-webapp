import os
import json

# Dictionary mapping county names to file paths
COUNTY_FILES = {
    "grand": "graphs_counties/Grand_County_Utah_USA_merged_offroad_legal.geojson",
    "sanjuan": "graphs_counties/San_Juan_County_Utah_USA_merged_offroad_legal.geojson",
    "emery": "graphs_counties/Emery_County_Utah_USA_offroad_legal.geojson",
}

# Output file for the merged GeoJSON
OUTPUT_FILE = "merged_all_counties.geojson"

# Initialize an empty list to collect all features
merged_features = []

# Iterate over each county file and merge features
for county, filepath in COUNTY_FILES.items():
    if os.path.exists(filepath):
        print(f"Loading {county} from {filepath}...")
        with open(filepath, "r") as f:
            geojson_data = json.load(f)
            # Ensure the file is a FeatureCollection and has features
            if geojson_data.get("type") == "FeatureCollection" and "features" in geojson_data:
                merged_features.extend(geojson_data["features"])
            else:
                print(f"Warning: {filepath} is not a valid FeatureCollection.")
    else:
        print(f"Error: File not found: {filepath}")

# Create the merged GeoJSON structure
merged_geojson = {
    "type": "FeatureCollection",
    "features": merged_features
}

# Write the merged GeoJSON to the output file
with open(OUTPUT_FILE, "w") as out_file:
    json.dump(merged_geojson, out_file, indent=2)

print(f"Merged GeoJSON written to {OUTPUT_FILE}")
