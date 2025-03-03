#!/usr/bin/env python3
"""
Merge two GeoJSON files by updating properties in the base file with values from the export file.
Features are matched by comparing their geometry (using their WKT representation).
Only fields that already exist in the base file are updated:
  - If the export value is not null, it replaces the base value.
  - Otherwise, the base value is kept.
No new fields are added.

Usage:
    python merge_geojson.py

Make sure the two files (e.g., "grand_county.geojson" and "export.geojson")
are in the same directory as this script or adjust the paths accordingly.
"""

import geopandas as gpd
import pandas as pd

# File paths: update these as necessary.
BASE_FILE = "grand_county.geojson"     # The file with the existing county data.
EXPORT_FILE = "export.geojson"           # The file exported from Overpass Turbo.
OUTPUT_FILE = "merged.geojson"           # The output file after merging.

def merge_geojson(base_file, export_file, output_file):
    # Read both GeoJSON files into GeoDataFrames.
    gdf_base = gpd.read_file(base_file)
    gdf_export = gpd.read_file(export_file)

    # Create a string representation of geometry to use as a key.
    # This assumes that features which represent the same route have identical WKT.
    gdf_base["geom_key"] = gdf_base.geometry.apply(lambda g: g.wkt)
    gdf_export["geom_key"] = gdf_export.geometry.apply(lambda g: g.wkt)

    # Set the index to the geom_key for easier matching.
    gdf_base = gdf_base.set_index("geom_key")
    gdf_export = gdf_export.set_index("geom_key")

    # Get the common keys (i.e. features that exist in both files).
    common_keys = gdf_base.index.intersection(gdf_export.index)

    # For each matching feature, update the base properties with non-null export values.
    for key in common_keys:
        # For each column in the base data (excluding geometry; you can keep geometry as is)
        for col in gdf_base.columns:
            if col == "geometry":
                continue
            # Only update if the export GeoDataFrame also has that column.
            if col in gdf_export.columns:
                export_val = gdf_export.loc[key, col]
                # If export_val is not null, update the base value.
                # We use pd.notnull to handle NaN and None.
                if pd.notnull(export_val):
                    gdf_base.at[key, col] = export_val

    # Reset index and drop the helper column.
    gdf_merged = gdf_base.reset_index(drop=True)
    
    # Write the merged GeoDataFrame to a new GeoJSON file.
    gdf_merged.to_file(output_file, driver="GeoJSON")
    print(f"Merge complete. Merged file saved as {output_file}")

if __name__ == "__main__":
    merge_geojson(BASE_FILE, EXPORT_FILE, OUTPUT_FILE)
