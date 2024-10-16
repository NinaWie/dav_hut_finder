"""Serves public_transport_airbnb backend with flask."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Text

import geopandas as gpd
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS, cross_origin

from filtering import filter_huts

app = Flask(__name__, static_folder="static")

CORS(app, origins=["*", "null"])  # allowing any origin as well as localhost (null)

# if set to true, check on the fly whether the huts are available (might take a while)
# if false, load precomputed availability table
ONLINE_AVAIL_CHECK = False
# if false, need to set path to availability file
AVAIL_PATH = os.path.join("data", "availability.csv")
# debug mode: directly return rendered html table
DEBUG = False

# load huts database
huts = gpd.read_file(os.path.join("data", "huts_database.geojson"))


@app.route("/")
def serve_index():
    """Serve index page."""
    return send_from_directory(app.static_folder, "index_python_app.html")


@app.route("/<path:path>")
def serve_static_files(path: Path):
    """Serves files from static folder."""
    return send_from_directory(app.static_folder, path)


@cross_origin()
@app.route("/api/markers")
def markers():
    """Publish example marker data."""
    markers_data = [
        {"id": 1, "name": "Marker 1", "position": [46.5, 10.5]},
        {"id": 2, "name": "Marker 2", "position": [45.8326, 6.8652]},
        {"id": 3, "name": "Marker 3", "position": [45.9763, 7.6586]},
        {"id": 4, "name": "Marker 4", "position": [47.4210, 10.9849]},
    ]
    return jsonify(markers_data)


def convert_to_float(request: request, col_name: Text, default: float) -> float:
    """
    Convert to float with error check.

    Args:
        request: flask request
        col_name: column name
        default: default value to return when conversion fails

    Returns:
        float if no error occurred. Otherwise return default
    """
    try:
        return float(request.args.get(col_name, default))
    except ValueError:
        return default


def availability_as_html(availability: pd.DataFrame, filtered_huts: pd.DataFrame) -> Any:
    """
    Return availability as HTML table (deprecated).

    Args:
        availability (pd.DataFrame): availability dataframe
        filtered_huts (pd.DataFrame): filtered huts dataframe
    Returns:
        HTML table
    """
    # merge availability with filtered
    all_huts_with_availability = pd.merge(filtered_huts, availability, how="left", left_on="id", right_on="id")
    # remove unattended operation
    all_huts_with_availability = all_huts_with_availability[
        all_huts_with_availability["room_type"] != "Unattended operation"
    ]
    # remove unnecessary columns and format
    result = (
        all_huts_with_availability.set_index(["name", "altitude", "verein", "distance", "room_type"])
        .swapaxes(1, 0)
        .drop(
            [
                "latitude",
                "longitude",
                "geometry",
                "Unnamed: 0",
                "sektion",
                "name_original",
                "hut_warden",
                "phone",
                "total_places",
                "coordinates",
                "id",
                "altitude_m",
            ],
            errors="ignore",
        )
    )
    return render_template("simple.html", tables=[result.to_html(classes="data")], titles=result.columns.values)


def table_to_dict(table: pd.DataFrame) -> [Dict]:
    """
    Converts pandas dataframe to list of dicts.

    Args:
        table: pandas dataframe

    Returns:
        List of dicts
    """
    if table.index.name is not None:
        table.reset_index(inplace=True)
    table.drop(["geometry"], axis=1, errors="ignore", inplace=True)
    return [row.to_dict() for _, row in table.iterrows()]


@app.route("/api/submit", methods=["POST"])
def submit():
    """Handle submit request on button activation."""
    data = request.json

    # Convert strings to floats and date string to datetime object
    filter_attributes = {
        "start_lat": float(data["latitude"]),
        "start_lon": float(data["longitude"]),
        "min_distance": float(data["minDistance"]),
        "max_distance": float(data["maxDistance"]),
        "min_altitude": float(data["minAltitude"]),
        "max_altitude": float(data["maxAltitude"]),
    }

    # filter huts by distance from start etc
    filtered_huts = filter_huts(huts, **filter_attributes)

    # get inputs for checking date availability (need to convert to datetime and back for correct format)
    check_data_datetime = datetime.strptime(data["date"], "%Y-%m-%d")
    check_date = check_data_datetime.strftime("%d.%m.%Y")
    min_avail_spaces = float(data.get("minSpaces", 1))

    # filter by availability
    if check_date not in ["None", ""] and os.path.exists(AVAIL_PATH):
        # load availability (cannot preload it because it is updated daily)
        availability = pd.read_csv(AVAIL_PATH)

        if DEBUG:
            return availability_as_html(availability, filtered_huts)

        if check_date not in availability.columns:
            return jsonify({"status": "error", "message": "Date not available"})

        # check availability with date
        availability = (pd.read_csv(AVAIL_PATH)[["id", "room_type", check_date]]).rename(
            {check_date: "availability"}, axis=1
        )
        availability.dropna(subset=["availability"], inplace=True)
        availability["available_spaces"] = (availability["availability"].str.split(" ").str[0]).astype(int)
        # sum up availability for all room types
        availability = availability.groupby("id")["available_spaces"].sum().reset_index()

        huts_with_availability = pd.merge(filtered_huts, availability, how="left", left_on="id", right_on="id")
        huts_with_availability = huts_with_availability[huts_with_availability["available_spaces"] > min_avail_spaces]
        return jsonify({"status": "success", "markers": table_to_dict(huts_with_availability)})

    # just return filtered huts without availability check
    else:
        if DEBUG:
            return render_template(
                "simple.html", tables=[filtered_huts.to_html(classes="data")], titles=filtered_huts.columns.values
            )
        return jsonify({"status": "success", "markers": table_to_dict(filtered_huts)})


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5555)
