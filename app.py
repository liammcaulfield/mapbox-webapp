from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Path to the merged GeoJSON file
MERGED_FILE = "merged_all_counties.geojson"
# Path to the waypoints GeoJSON file
WAYPOINTS_FILE = "filtered_waypoints.geojson"

@app.route("/offroad_edges/merged")
def merged_offroad_edges():
    """
    Serve the merged GeoJSON file that contains all counties.
    """
    if not os.path.exists(MERGED_FILE):
        app.logger.error(f"🚨 Merged file not found: {MERGED_FILE}")
        return jsonify({"error": "Merged file not found"}), 404

    app.logger.info(f"📂 Serving merged file: {MERGED_FILE}")
    with open(MERGED_FILE, "r") as f:
        geojson_data = json.load(f)

    return jsonify(geojson_data)

@app.route("/waypoints")
def waypoints():
    """
    Serve the waypoints GeoJSON file.
    """
    if not os.path.exists(WAYPOINTS_FILE):
        app.logger.error(f"🚨 Waypoints file not found: {WAYPOINTS_FILE}")
        return jsonify({"error": "Waypoints file not found"}), 404

    app.logger.info(f"📂 Serving waypoints file: {WAYPOINTS_FILE}")
    with open(WAYPOINTS_FILE, "r") as f:
        geojson_data = json.load(f)

    return jsonify(geojson_data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
