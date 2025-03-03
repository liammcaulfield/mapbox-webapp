# fetch_waypoints.py

from osmnx.features import features_from_place
import geopandas as gpd

def fetch_waypoints(place_name, out_geojson):
    """
    Fetch POIs from OSM in the specified place, focusing on hot springs,
    viewpoints, campgrounds, etc. Then save to GeoJSON.
    """
    # 1) Define the OSM tags you want:

    tags = {
    "natural": [
        "hot_spring",     # Natural hot springs
        "spring",         # Freshwater springs
        "peak",           # Mountain peaks
        "waterfall",      # Waterfalls
        "rock",           # Rock formations
        "cave_entrance"   # Cave entrances
    ],
    "tourism": [
        "viewpoint",      # Scenic overlooks
        "camp_site",      # Campgrounds
        "picnic_site",    # Picnic areas
        "attraction",     # Generic tourist attractions
        "museum",         # Museums
        "gallery",        # Art galleries
        "information"     # Info boards, visitor centers (may need sub-tag)
    ],
    "amenity": [
        "drinking_water", # Drinking water taps
        "toilets",        # Public toilets
        "fuel",           # Gas stations
        "ranger_station", # Ranger stations
        "parking",        # Parking lots
        "restaurant",     # Restaurants
        "cafe"            # Cafes
    ],
    "historic": [
        "yes",            # Generic fallback for all historic features
        "ruins",          # Archaeological or structural ruins
        "monument",       # Monuments, memorials
        "archaeological_site" # Officially tagged archaeological areas
    ],
    "leisure": [
        "park",           # Formal parks
        "nature_reserve"  # Nature reserves/protected areas
    ],
    "sport": "climbing",  # Rock climbing sites
    "man_made": "tower",  # Observation towers, etc.
    "shop": [
        "outdoor",        # Outdoor gear shops
        "bicycle",        # Bike shops
        "sports"          # General sports shops
    ],
    "emergency": "phone", # Emergency phones in remote areas
    "healthcare": [
        "hospital",       # Hospitals
        "clinic",         # Clinics
        "pharmacy"        # Pharmacies
    ]
}


    # 2) Fetch the features from place
    #    This returns a GeoDataFrame of points/lines/polygons matching these tags.
    print(f"Fetching waypoints for {place_name}...")
    gdf = features_from_place(place_name, tags)

    # 3) Filter to only points (if you want specifically node-based POIs).
    #    Some might be polygons (like campgrounds). You can decide to keep them.
    # gdf = gdf[gdf.geometry.type == "Point"]

    # 4) Save to GeoJSON
    gdf.to_file(out_geojson, driver="GeoJSON")
    print(f"✅ Saved {len(gdf)} waypoints to {out_geojson}")

if __name__ == "__main__":
    # Example usage:
    # If you want Grand County, UT
    place = "San_Juan_County, Utah, USA"
    out_file = "san_juan_county_waypoints.geojson"
    fetch_waypoints(place, out_file)
