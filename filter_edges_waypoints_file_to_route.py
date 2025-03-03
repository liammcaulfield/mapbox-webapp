import geopandas as gpd
from shapely.geometry import Polygon

# Coordinates in (longitude, latitude) format.
coords = [
    (-109.790220, 38.518660),
    (-109.655685, 38.485290),
    (-109.649959, 38.156585),
    (-109.831324, 38.148435)
]

# Create the bounding polygon
area_polygon = Polygon(coords)

# Load the original waypoints
waypoints_file = "san_juan_county_waypoints.geojson"
waypoints_data = gpd.read_file(waypoints_file)

# Ensure EPSG:4326
if waypoints_data.crs is None:
    waypoints_data.set_crs(epsg=4326, inplace=True)
elif waypoints_data.crs.to_string() != "EPSG:4326":
    waypoints_data = waypoints_data.to_crs(epsg=4326)

# 1) Keep only those strictly within the polygon
filtered_waypoints = waypoints_data[waypoints_data.within(area_polygon)]
print(f"Waypoints after within() filtering: {len(filtered_waypoints)}")

# 2) Remove any with name == 'N/A'
if "name" in filtered_waypoints.columns:
    original_count = len(filtered_waypoints)
    # Keep only rows where "name" is not null.
    filtered_waypoints = filtered_waypoints[filtered_waypoints["name"].notnull()]
    removed_count = original_count - len(filtered_waypoints)
    print(f"Removed {removed_count} waypoints with name=null.")

# 3) Remove any with "nam" == null (i.e., None)
if "nam" in filtered_waypoints.columns:
    original_count = len(filtered_waypoints)
    # GeoPandas uses .notnull() to check for non-null values
    filtered_waypoints = filtered_waypoints[filtered_waypoints["nam"].notnull()]
    removed_count = original_count - len(filtered_waypoints)
    print(f"Removed {removed_count} waypoints with nam=null.")

print(f"Final waypoints count: {len(filtered_waypoints)}")

# Write final
filtered_waypoints.to_file("filtered_waypoints.geojson", driver="GeoJSON")
print("Saved to filtered_waypoints.geojson")
