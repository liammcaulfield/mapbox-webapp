#!/usr/bin/env python3
"""
Download offroad roads for specific counties in Utah using OSMnx's geometries_from_polygon,
with a custom filter ensuring legal public access and offroad surfaces.
This version includes:
- Automatic subdivision of slow query areas
- Increased Overpass memory/time limits
- Alternative Overpass server for better performance
- Creating a new subfolder for each county under the "graphs_counties" folder,
  and saving the merged GeoJSON file inside that county's folder.
  
The custom filter now matches the Overpass Turbo query:
  - highway: track|unclassified|service|path|bridleway|tertiary|secondary
  - access: not private, customers, or restricted (applied as a post-filter)
  - surface: gravel, dirt, or unpaved
Any additional tags (e.g., tracktype, grade) will be returned if available.
"""

import os
import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from time import time

# Configure Overpass API settings
ox.settings.overpass_timeout = 600         # Increase timeout to 10 minutes
ox.settings.overpass_memory = 2147483648     # Increase Overpass memory to 2GB
ox.settings.max_query_area_size = 5e8        # Helps prevent excessive subdivisions

# Optional: Change Overpass API endpoint for better speed (comment out if using default)
# ox.settings.overpass_endpoint = "http://overpass.kumi.systems/api/interpreter"

# List of counties to process
LARGE_COUNTIES = [
    "Grand County, Utah, USA",
    "San Juan County, Utah, USA",
]

# Default grid size for county subdivision
GRID_ROWS, GRID_COLS = 4, 4

# Define tags for geometry extraction (this does not force existence of tracktype, but returns it if present)
TAGS = {
    "highway": ["track", "unclassified", "service", "path", "bridleway", "tertiary", "secondary"],
    "surface": ["gravel", "dirt", "unpaved"]
}

def create_county_folder(county_name):
    """Creates a subfolder under 'graphs_counties' for the county."""
    safe_county = county_name.replace(',', '').replace(' ', '_')
    folder_path = os.path.join("graphs_counties", safe_county)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def subdivide_county(county_name, rows=4, cols=4):
    """Splits a county's bounding box into smaller grid areas."""
    county_gdf = ox.geocode_to_gdf(county_name)
    county_polygon = county_gdf.iloc[0].geometry
    minx, miny, maxx, maxy = county_polygon.bounds

    x_steps = [minx + i * (maxx - minx) / cols for i in range(cols + 1)]
    y_steps = [miny + j * (maxy - miny) / rows for j in range(rows + 1)]
    sub_polys = []

    for i in range(cols):
        for j in range(rows):
            cell = box(x_steps[i], y_steps[j], x_steps[i + 1], y_steps[j + 1])
            intersection = cell.intersection(county_polygon)
            if not intersection.is_empty:
                sub_polys.append(intersection)

    return sub_polys

def download_offroad_for_polygon(polygon, county_name, idx):
    """Downloads offroad data for a specific polygon grid piece as a GeoDataFrame."""
    try:
        print(f"🔹 Starting download for {county_name}, piece {idx}...")
        start_time = time()

        # Extract all features matching the specified tags from the polygon.
        gdf = ox.geometries_from_polygon(polygon, tags=TAGS)

        elapsed_time = time() - start_time
        print(f"⏱️ Download time: {elapsed_time:.2f} sec")

        if gdf.empty:
            print(f"⚠️ No data returned for {county_name} piece {idx}.")
            return None

        # Filter out features where access is restricted.
        # Keep features where "access" is either missing or not one of the restricted values.
        if "access" in gdf.columns:
            gdf = gdf[(gdf["access"].isna()) | (~gdf["access"].str.lower().isin(["private", "customers", "restricted"]))]

        # Create the county folder.
        county_folder = create_county_folder(county_name)
        out_file = os.path.join(county_folder, f"{county_folder.split(os.sep)[-1]}_piece_{idx}_offroad_legal.geojson")
        gdf.to_file(out_file, driver="GeoJSON")
        print(f"✅ Finished {county_name} piece {idx}. Saved to {out_file}\n")

        return gdf

    except Exception as e:
        print(f"❌ Error downloading {county_name} piece {idx}: {e}")
        return None

def process_large_county(county_name, rows=GRID_ROWS, cols=GRID_COLS):
    """Processes a large county by subdividing it and downloading each grid section."""
    print(f"📌 Subdividing {county_name} into {rows}x{cols} grid...")
    sub_polys = subdivide_county(county_name, rows, cols)
    gdf_list = []

    for idx, poly in enumerate(sub_polys, start=1):
        gdf = download_offroad_for_polygon(poly, county_name, idx)
        if gdf is None:
            print(f"🔄 Re-processing {county_name}, piece {idx} with finer grid...")
            finer_subdivisions = subdivide_county(county_name, rows=2, cols=2)
            for sub_idx, sub_poly in enumerate(finer_subdivisions, start=1):
                gdf = download_offroad_for_polygon(sub_poly, county_name, f"{idx}.{sub_idx}")
                if gdf is not None:
                    gdf_list.append(gdf)
        else:
            gdf_list.append(gdf)

    if gdf_list:
        # Merge all GeoDataFrames (if multiple pieces exist)
        merged_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))
        county_folder = create_county_folder(county_name)
        out_file = os.path.join(county_folder, f"{county_folder.split(os.sep)[-1]}_merged_offroad_legal.geojson")
        merged_gdf.to_file(out_file, driver="GeoJSON")
        print(f"✅ Merged GeoDataFrame for {county_name} saved to {out_file}\n")
    else:
        print(f"❌ No data downloaded for {county_name}.")

if __name__ == "__main__":
    for county in LARGE_COUNTIES:
        process_large_county(county)

    try:
        county = "Emery County, Utah, USA"
        print(f"🔹 Starting download for {county}...")
        county_folder = create_county_folder(county)
        gdf = ox.geometries_from_place(county, tags=TAGS)
        if "access" in gdf.columns:
            gdf = gdf[(gdf["access"].isna()) | (~gdf["access"].str.lower().isin(["private", "customers", "restricted"]))]
        out_file = os.path.join(county_folder, f"{county_folder.split(os.sep)[-1]}_offroad_legal.geojson")
        gdf.to_file(out_file, driver="GeoJSON")
        print(f"✅ Finished {county}. Saved to {out_file}\n")
    except Exception as e:
        print(f"❌ Error downloading {county}: {e}")

    print("🎉 All downloads complete!")
