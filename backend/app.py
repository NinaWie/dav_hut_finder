"""Serves public_transport_airbnb backend with flask."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Text

import geopandas as gpd
import pandas as pd
import psycopg2
import sqlalchemy
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine

from .filtering import filter_huts, multi_day_route_finding

app = Flask(__name__, static_folder="static")

CORS(app, origins=["*", "null"])  # allowing any origin as well as localhost (null)

# if set to true, check on the fly whether the huts are available (might take a while)
# if false, load precomputed availability table
ONLINE_AVAIL_CHECK = False
# db login for database
DB_LOGIN_PATH = "db_login.json"
# debug mode: directly return rendered html table
DEBUG = False

with open(DB_LOGIN_PATH, "r") as infile:
    db_credentials = json.load(infile)


def get_con():
    """Initialize connection to database."""
    return psycopg2.connect(**db_credentials)


try:
    engine = create_engine("postgresql+psycopg2://", creator=get_con)
except sqlalchemy.exc.OperationalError as err:
    raise RuntimeError("Database issue: No connection can be established! Check login and database server") from err


# load huts database
huts = gpd.read_file(os.path.join("data", "huts_database.geojson"))
id_to_hut_name = huts.set_index("id")["name"].to_dict()


def get_availability_for_dates(dates: list, min_places: int = 1) -> pd.DataFrame:
    """Get table with number of available places for each hut on a given date."""
    # create engine
    engine = create_engine("postgresql+psycopg2://", creator=get_con)
    # load availability
    date_str = "date='" + "' OR date='".join(dates) + "'"
    availability = pd.read_sql(
        f"SELECT hut_id, date, places_avail FROM hut_availability WHERE places_avail>={min_places} AND ({date_str})",
        engine,
    )
    return availability


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

    # get inputs for checking date availability (need to convert to datetime and back for correct format)
    check_date_str = data.get("date", None)
    # min_avail_spaces = int(data.get("minSpaces", 1))

    # filter huts by distance from start etc
    filtered_huts = filter_huts(huts, **filter_attributes)
    filtered_huts["link"] = filtered_huts["id"].apply(
        lambda x: f"https://www.hut-reservation.org/reservation/book-hut/{x}/wizard"
    )
    filtered_huts["verein"] = filtered_huts["verein"].fillna("-")

    # filter by availability
    if check_date_str is not None:
        # transform check date
        check_date_datetime = datetime.strptime(check_date_str, "%Y-%m-%d")
        check_date = check_date_datetime.strftime("%d.%m.%Y")

        # load availability (cannot preload it because it is updated daily)
        availability = get_availability_for_dates([check_date])

        if DEBUG:
            return availability_as_html(availability, filtered_huts)

        # # version 1
        # availability.rename({check_date: "availability"}, axis=1, inplace=True)
        # availability.dropna(subset=["availability"], inplace=True)
        # availability["available_spaces"] = (availability["availability"].str.split(" ").str[0]).astype(int)
        # # sum up availability for all room types
        # availability = availability.groupby("id")["available_spaces"].sum().reset_index()

        # add places_avail column to filtered huts
        huts_filtered_and_available = filtered_huts.merge(availability, left_on="id", right_on="hut_id", how="left")
        # fill nans
        huts_filtered_and_available["places_avail"] = huts_filtered_and_available["places_avail"].fillna(-1)
        huts_filtered_and_available = huts_filtered_and_available.fillna("-")
        # huts_filtered_and_available = filtered_huts[filtered_huts["id"].isin(available_huts["hut_id"])]
        return jsonify({"status": "success", "markers": table_to_dict(huts_filtered_and_available)})

    # just return filtered huts without availability check
    else:
        if DEBUG:
            return render_template(
                "simple.html", tables=[filtered_huts.to_html(classes="data")], titles=filtered_huts.columns.values
            )
        return jsonify({"status": "success", "markers": table_to_dict(filtered_huts)})


@app.route("/api/multi_day", methods=["POST"])
def multi_day_planning():
    """Handle multi-day planning request."""
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
    # construct list of dates
    date_list = [data["date1"], data["date2"], data["date3"], data["date4"], data["date5"]]
    date_list = [d for d in date_list if d is not None]
    assert len(date_list) > 1, "There must be at least two dates for multi-day planning"

    # get availability for all dates
    availability_from_database = get_availability_for_dates(date_list, int(data["minSpaces"]))
    avail_per_date = availability_from_database.pivot(index="hut_id", columns="date", values="places_avail")

    # filter huts by distance from start etc
    filtered_hut_ids = filter_huts(huts, **filter_attributes)["id"]
    avail_per_date = avail_per_date[avail_per_date.index.isin(filtered_hut_ids)]

    # load feasible connections - NOTE: preload this to speed up the process
    feasible_connections = pd.read_csv(os.path.join("data", "feasible_connections.csv"), index_col="id_source")

    # compute trip options
    trip_options = multi_day_route_finding(date_list, feasible_connections, avail_per_date, id_to_hut_name)

    # convert to dicts
    huts_with_id = huts.set_index("id")
    nr_days = len(date_list)
    json_dicts = []
    for _, row in trip_options.iterrows():
        # make list of coordinates
        coordinates = [
            [huts_with_id.loc[row[f"day{k}"], "latitude"], huts_with_id.loc[row[f"day{k}"], "longitude"]]
            for k in range(nr_days)
        ]
        # combine names, places and distances
        infos = " -> ".join(
            [row[f"name_day{k}"] + "(" + str(int(row[f"places_day{k}"])) + " spots)" for k in range(nr_days)]
        )
        dist = ", ".join([str(round(row[f"distance_day{k}"] / 1000, 2)) + " km" for k in range(1, nr_days)])
        json_dicts.append({"infos": infos, "coordinates": coordinates, "distance": dist})

    return jsonify({"status": "success", "polylines": json_dicts})


def create_app():
    """Create app for waitress."""
    return app


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5555)
