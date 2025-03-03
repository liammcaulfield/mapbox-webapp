#!/usr/bin/env python3
"""
Enrich offroad routes for specific counties in Utah using a local OSM PBF file,
Pyrosm, OSMnx, and GeoPandas, with a custom filter.

This script:
  - Loads a local PBF file (using a full path, e.g., "/Users/baguettebandit/onx-offroad-route/data/utah.osm.pbf").
  - Uses OSMnx to retrieve county boundaries.
  - Uses Pyrosm's get_data_by_custom_criteria() to extract highway features
    (with highway values matching our criteria) from the entire PBF file.
  - Clips the extracted features to the county boundary.
  - Applies additional post-filters to enforce:
      • "motor_vehicle" is not "no",
      • "access" is not "private", "customers", or "restricted",
      • "surface" is one of "gravel", "dirt", or "unpaved".
  - Merges the results and writes out an enriched GeoJSON file.
  
Ensure:
  - You have installed Pyrosm (pip install pyrosm), OSMnx, GeoPandas, and pandas.
  - You have downloaded an OSM PBF file (e.g., for Utah) and set the correct full path.
"""

import os
import osmnx as ox
import geopandas as gpd
import pandas as pd
from pyrosm import OSM

# List of counties to process
COUNTIES = [
    "Grand County, Utah, USA",
    "San Juan County, Utah, USA",
    "Emery County, Utah, USA"
]

# Full path to the local OSM PBF file
PBF_FILE = "/Users/baguettebandit/onx-offroad-route/data/utah.osm.pbf"

# Define the highway values to include (from your custom filter)
HIGHWAY_VALUES = ["track", "unclassified", "service", "path", "bridleway", "tertiary", "secondary"]

def post_filter(df):
    """
    Post-filter the GeoDataFrame to meet the following conditions:
      - "motor_vehicle" must not equal "no" (or be missing)
      - "access" must not be "private", "customers", or "restricted" (or be missing)
      - "surface" must be one of "gravel", "dirt", or "unpaved" (feature is dropped if missing)
    """
    cond_motor = df["motor_vehicle"].isna() | (df["motor_vehicle"].str.lower() != "no")
    cond_access = df["access"].isna() | (~df["access"].str.lower().isin(["private", "customers", "restricted"]))
    cond_surface = df["surface"].str.lower().isin(["gravel", "dirt", "unpaved"])
    return df[cond_motor & cond_access & cond_surface]

# Output merged enriched GeoJSON file
OUTPUT_FILE = "merged_all_counties_enriched_custom.geojson"

def process_county(county_name):
    """Extract and enrich offroad routes for a single county."""
    print(f"Processing {county_name}...")
    
    # Get the county boundary using OSMnx
    county_gdf = ox.geocode_to_gdf(county_name)
    if county_gdf.empty:
        print(f"❌ Could not geocode {county_name}. Skipping.")
        return None
    county_polygon = county_gdf.iloc[0].geometry

    # Initialize Pyrosm with the local PBF file
    osm = OSM(PBF_FILE)

    # Extract all highway features that match our desired highway values from the entire file.
    roads = osm.get_data_by_custom_criteria(
        custom_filter={"highway": HIGHWAY_VALUES},
        osm_keys_to_keep="all"
    )
    if roads is None or roads.empty:
        print(f"⚠️ No road data found for {county_name} in the PBF file.")
        return None

    # Ensure the GeoDataFrame has a valid CRS; assume EPSG:4326 if missing.
    if roads.crs is None:
        roads.set_crs(epsg=4326, inplace=True)
    
    # Clip the roads to the county boundary.
    roads_clipped = gpd.clip(roads, county_polygon)
    if roads_clipped.empty:
        print(f"⚠️ No features remain after clipping for {county_name}.")
        return None

    # Apply post-filters to enforce motor_vehicle, access, and surface conditions.
    roads_filtered = post_filter(roads_clipped)
    if roads_filtered.empty:
        print(f"⚠️ No features passed post-filter for {county_name}.")
        return None

    # Optionally add the county name as an attribute.
    roads_filtered["county"] = county_name

    print(f"✅ {county_name}: {len(roads_filtered)} features extracted and enriched.")
    return roads_filtered

def main():
    enriched_dfs = []
    for county in COUNTIES:
        gdf = process_county(county)
        if gdf is not None and not gdf.empty:
            enriched_dfs.append(gdf)
    if enriched_dfs:
        merged_gdf = gpd.GeoDataFrame(pd.concat(enriched_dfs, ignore_index=True))
        merged_gdf = merged_gdf.to_crs(epsg=4326)
        merged_gdf.to_file(OUTPUT_FILE, driver="GeoJSON")
        print(f"🎉 Merged enriched GeoJSON saved to {OUTPUT_FILE}")
    else:
        print("❌ No data to merge.")

if __name__ == "__main__":
    main()
