#!/usr/bin/env python3

import json
from shapely.geometry import shape, LineString, MultiLineString
from shapely.ops import linemerge
from shapely.geometry import mapping

# Input file with multiple line features (leg1.geojson)
INPUT_FILE = "leg2.geojson"
# Output merged file (just one line)
OUTPUT_FILE = "leg2_merged.geojson"

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract shapely geometries from each feature
    lines = []
    for feature in data.get("features", []):
        geom = shape(feature["geometry"])
        lines.append(geom)

    # Merge lines
    # linemerge() will combine contiguous lines into a single (Multi)LineString.
    merged = linemerge(lines)

    # If the result is a MultiLineString (disconnected lines), you can handle it accordingly.
    # If it's guaranteed to be contiguous, you'll get a single LineString.
    if isinstance(merged, MultiLineString):
        print("Merged result is a MultiLineString with %d parts." % len(list(merged.geoms)))
        # If you want to treat them as separate or forcibly connect them, that's up to you.
        # Here, we just pick them all up as one feature in a MultiLineString geometry.
        merged_geom = merged
    else:
        print("Merged result is a single LineString.")
        merged_geom = merged

    # Create a single feature
    merged_feature = {
        "type": "Feature",
        "properties": {
            "name": "Leg 1 Merged"
        },
        "geometry": mapping(merged_geom)  # convert Shapely geometry back to geojson
    }

    # Build a FeatureCollection
    merged_collection = {
        "type": "FeatureCollection",
        "features": [merged_feature]
    }

    # Write to disk
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(merged_collection, out, indent=2, ensure_ascii=False)

    print(f"Done! Merged geometry written to {OUTPUT_FILE}.")

if __name__ == "__main__":
    main()
