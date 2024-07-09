"""Serves public_transport_airbnb backend with flask."""

import os
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
import geopandas as gpd
import numpy as np
import datetime
import pandas as pd

from filtering import filter_huts
from check_availability import AvailabilityChecker

app = Flask(__name__)
CORS(app, origins=["*", "null"])  # allowing any origin as well as localhost (null)

# if set to true, check on the fly whether the huts are available (might take a while)
# if false, load precomputed availability table
ONLINE_AVAIL_CHECK = False
# if false, need to set path to availability file
AVAIL_PATH = os.path.join("data", "availability.csv")

# load huts database
huts = gpd.read_file(os.path.join("data", "huts_database.geojson"))


@app.route("/")
def serve_index():
    """Serve index."""
    return send_from_directory("../frontend", "index.html")


def convert_to_float(request, col_name, default):
    try:
        return float(request.args.get(col_name, default))
    except ValueError:
        return default


@app.route("/get_filtered_huts", methods=["GET"])
def get_filtered_huts():
    """filter huts and get availability"""
    # start lat and lon
    start_lat = convert_to_float(request, "start_lat", np.nan)
    start_lon = convert_to_float(request, "start_lon", np.nan)
    # filtering arguments
    min_distance = convert_to_float(request, "min_distance", 0)
    max_distance = convert_to_float(request, "max_distance", np.inf)
    min_altitude = convert_to_float(request, "min_altitude", 0)
    max_altitude = convert_to_float(request, "max_altitude", np.inf)

    # filter huts by distance from start etc
    filtered_huts = filter_huts(
        huts,
        start_lat=start_lat,
        start_lon=start_lon,
        max_distance=max_distance,
        min_distance=min_distance,
        min_altitude=min_altitude,
        max_altitude=max_altitude,
    )

    # whether to check availability
    check_date = str(request.args.get("date", None))
    # filter by availability
    if check_date not in ["None", ""]:

        if ONLINE_AVAIL_CHECK:
            print(f"Checking {len(filtered_huts)} huts for availability")
            # initialize checker and scrape availability for all huts
            checker = AvailabilityChecker()
            result = checker.availability_specific_date(filtered_huts, check_date)
            checker.close()
        else:
            # load availability (cannot preload it because it is updated daily)
            availability = pd.read_csv(AVAIL_PATH)
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
                    ]
                )
            )

        # out put dictionary with key=huts and values=sum of available_beds
        return render_template("simple.html", tables=[result.to_html(classes="data")], titles=result.columns.values)

    else:
        # output dictionary with key=huts and values=distance from start location
        return render_template(
            "simple.html", tables=[filtered_huts.to_html(classes="data")], titles=filtered_huts.columns.values
        )


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8989)
