"""Serves public_transport_airbnb backend with flask."""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*", "null"])  # allowing any origin as well as localhost (null)


@app.route("/")
def serve_index():
    """Serve index."""
    return send_from_directory("../frontend", "index.html")


@app.route("/compute_route", methods=["GET"])
def compute_route():
    """Compute route given long and latitude."""
    start_lat = float(request.args.get("start_lat", 1))
    start_lon = float(request.args.get("start_lon", 2))
    print("Start coordinates:", start_lat, start_lon)
    return jsonify("dummy method cannot do anything yet")


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8989)
