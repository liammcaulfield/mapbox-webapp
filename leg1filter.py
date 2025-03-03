#!/usr/bin/env python3
import json
from shapely.geometry import shape, MultiLineString
from shapely.ops import linemerge, transform
from shapely.geometry import mapping
from pyproj import Transformer

INPUT_FILE = "merged_all_counties.geojson"
OUTPUT_FILE = "leg1.geojson"

# OSMIDs to merge
TARGET_OSMIDS = [10152689, 656971497]

# We'll transform from EPSG:4326 (lat/lon) to EPSG:32612 (UTM zone 12N)
# Adjust if you need a different local projection.
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32612", always_xy=True)

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    feats = data.get("features", [])

    # 1) Filter features
    selected = []
    for feat in feats:
        osmid_val = feat.get("properties", {}).get("osmid")
        if osmid_val in TARGET_OSMIDS:
            selected.append(feat)

    if not selected:
        print(f"No features found for OSMIDs: {TARGET_OSMIDS}")
        return

    # 2) Convert to Shapely geometries
    geoms = []
    for feat in selected:
        geoms.append(shape(feat["geometry"]))

    # 3) Merge them
    merged = linemerge(geoms)  # Could be a LineString or MultiLineString
    if isinstance(merged, MultiLineString):
        print("WARNING: Lines do not fully connect end-to-end. Result is a MultiLineString.")
    else:
        print("Merged into a single LineString.")

    # 4) Measure the distance in kilometers
    # Transform to UTM so .length is in meters
    merged_utm = transform(transformer.transform, merged)
    dist_m = merged_utm.length
    dist_km = dist_m / 1000.0
    print(f"Measured distance (UTM EPSG:32612): {dist_km:.2f} km")

    # 5) Create a single Feature
    merged_feature = {
        "type": "Feature",
        "properties": {
            "osmid_list": TARGET_OSMIDS,
            "note": "Merged lines for Leg 1",
            "length_km_utm": round(dist_km, 2)
        },
        "geometry": mapping(merged)
    }

    # 6) Write final FeatureCollection
    out_collection = {
        "type": "FeatureCollection",
        "features": [merged_feature]
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(out_collection, out, indent=2, ensure_ascii=False)

    print(f"Done! Wrote {OUTPUT_FILE} with measured distance of ~{dist_km:.2f} km.")

if __name__ == "__main__":
    main()
