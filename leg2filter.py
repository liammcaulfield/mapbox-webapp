#!/usr/bin/env python3

import json

# Input GeoJSON file
INPUT_FILE = "merged_all_counties.geojson"
# Output GeoJSON file (filtered for Leg 2)
OUTPUT_FILE = "leg2.geojson"

# The osmid/names to filter for Day 2
TARGET_FEATURES = [
    {"osmid": 656971497},
    {"osmid": 10146993,  "name": "Lockhart Basin Road"},  # existing
    {"osmid": 338701467, "name": "Lockhart Basin Road"},  # newly added
    {"osmid": 1134345068, "name": "Lockhart Basin Road"}, # newly added
    {"osmid": 339553881},                                 # no name constraint
    {"osmid": 339553875, "name": "Chicken Corners Trail"}
]

def is_target_feature(feature):
    """
    Return True if this feature's 'osmid' and optionally 'name'
    match one of the TARGET_FEATURES entries.
    """
    props = feature.get("properties", {})
    feat_osmid = props.get("osmid")
    feat_name = props.get("name")

    for tf in TARGET_FEATURES:
        # If 'name' is specified, match both osmid + name
        # If 'name' is omitted, match only osmid
        if "name" in tf:
            if feat_osmid == tf["osmid"] and feat_name == tf["name"]:
                return True
        else:
            if feat_osmid == tf["osmid"]:
                return True
    return False

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter down to only our Day 2 features
    original_features = data.get("features", [])
    filtered_features = [feat for feat in original_features if is_target_feature(feat)]

    # Build a new FeatureCollection
    filtered_collection = {
        "type": "FeatureCollection",
        "features": filtered_features
    }

    # Write out
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(filtered_collection, out, ensure_ascii=False, indent=2)

    print(f"Done! Found {len(filtered_features)} Day 2 features. Wrote {OUTPUT_FILE}.")

if __name__ == "__main__":
    main()
