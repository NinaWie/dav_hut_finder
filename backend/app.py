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
    print("start")
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
    if check_date != "None":
        print(f"Checking {len(filtered_huts)} huts for availability")
        # convert date into datetime object
        date_object = datetime.datetime.strptime(check_date, "%d.%m.%Y")

        # initialize checker
        checker = AvailabilityChecker()

        all_avail = []
        # iterate over all filtered huts
        for _, row in filtered_huts.iterrows():
            hut_name = row["name"]
            hut_id = row["id"]

            out_df = checker(hut_id, date_object)
            if len(out_df) > 0:
                out_df.index.name = "room_type"
                out_df.reset_index(inplace=True)
                out_df["hut_name"] = hut_name
            # # uncomment to save hut results as separate files
            # out_df.to_csv(f"outputs_new/{hut_id}.csv")
            all_avail.append(out_df)
        all_avail = pd.concat(all_avail)

        checker.close()

        # sum up beds available on the specific date
        result = checker.availability_specific_date(all_avail, check_date)

        # out put dictionary with key=huts and values=sum of available_beds
        return jsonify(result)

    else:
        # output dictionary with key=huts and values=distance from start location
        return render_template(
            "simple.html", tables=[filtered_huts.to_html(classes="data")], titles=filtered_huts.columns.values
        )


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8989)
