import osmnx as ox
from osmnx.convert import graph_to_gdfs
import geopandas as gpd
import json

def convert_graph_to_geojson(graphml_path, out_path):
    """
    Converts a GraphML file to a GeoJSON file while preserving all attributes.
    Ensures EPSG:4326 projection for Mapbox compatibility.
    """
    print(f"🔹 Converting {graphml_path} to GeoJSON...")

    # Load the GraphML file
    G = ox.load_graphml(graphml_path)

    # Convert to GeoDataFrames (nodes and edges)
    gdf_nodes, gdf_edges = graph_to_gdfs(G)

    # Ensure CRS is EPSG:4326 (Mapbox-compatible)
    gdf_edges = gdf_edges.to_crs("EPSG:4326")

    # Save edges to GeoJSON with all attributes
    gdf_edges.to_file(out_path, driver="GeoJSON")

    print(f"✅ Saved {out_path}")


if __name__ == "__main__":
    # List of GraphML files to convert
    graphml_files = [
        "graphs_counties/Grand_County_Utah_USA_merged_offroad_legal.graphml",
        "graphs_counties/San_Juan_County_Utah_USA_merged_offroad_legal.graphml",
        "graphs_counties/Emery_County_Utah_USA_offroad_legal.graphml"
    ]

    # Convert each file
    for graphml_file in graphml_files:
        geojson_file = graphml_file.replace(".graphml", ".geojson")
        convert_graph_to_geojson(graphml_file, geojson_file)

    print("🎉 All conversions complete!")
