"""filtering.py implements functions to filter huts by user input."""

from datetime import datetime, timedelta

import geopandas as gpd
import numpy as np
import pandas as pd
from haversine import haversine

DATE_FORMAT_IN, DATE_FORMAT_OUT = "%Y-%m-%d", "%d.%m.%Y"


def filter_huts(
    huts: gpd.GeoDataFrame,
    start_lat: float = None,
    start_lon: float = None,
    min_distance: int = 0,
    max_distance: int = np.inf,
    min_altitude: int = 0,
    max_altitude: int = np.inf,
    min_places: int = 0,
    max_places: int = np.inf,
    verbose: bool = False,
) -> gpd.GeoDataFrame:
    """
    Filter huts by user input.

    Args:
        huts: gpd.GeoDataFrame containing all hut information
        start_lat: starting latitude
        start_lon: starting longitude
        min_distance: minimum distance to next hut
        max_distance: maximum distance to next hut
        min_altitude: minimum altitude of huts
        max_altitude: maximum altitude of huts
        min_places: minimum number of spaces in the hut
        max_places: maximum number of spaces in the hut (e.g. for avoiding very large huts)
        verbose: verbose debug output

    Returns:
       gpd.GeoDataFrame containing filtered huts
    """

    def comp_haversine(row: gpd.GeoDataFrame) -> float:
        """
        Computes beeline distance in km.

        Args:
            row: gpd.GeoDataFrame

        Return:
            floating point distance
        """
        return haversine((row["latitude"], row["longitude"]), (start_lat, start_lon))

    if min_distance > 0 or max_distance < np.inf:
        assert start_lat is not None and start_lon is not None, "lat and lon must be provided if filtering for distance"
    # conditions for altitude and places
    min_alt_cond = huts["altitude_m"] >= min_altitude
    max_alt_cond = huts["altitude_m"] < max_altitude
    min_place_cond = huts["total_places"] >= min_places
    max_place_cond = huts["total_places"] < max_places
    huts_filtered = huts[min_alt_cond & max_alt_cond & min_place_cond & max_place_cond]
    if verbose:
        print(len(huts_filtered), "left after filtering (initially", len(huts))

    # check if we need to filter by distance
    if start_lat is not None and (max_distance < np.inf or min_distance > 0):
        # compute haversine distance between the huts and the starting location
        huts_filtered["distance"] = huts_filtered.apply(comp_haversine, axis=1)
        # filter by distance
        huts_filtered = huts_filtered[
            (huts_filtered["distance"] <= max_distance) & (huts_filtered["distance"] >= min_distance)
        ]
        huts_filtered["distance"] = huts_filtered["distance"].astype(int)
        if verbose:
            print(len(huts_filtered), "left after distance filtering (initially", len(huts))
    else:
        huts_filtered["distance"] = pd.NA

    return huts_filtered


def multi_day_route_finding(
    date_list: list[str],
    feasible_connections: pd.DataFrame,
    avail_per_date: pd.DataFrame,
    id_to_hut: dict,
    require_unique_huts: bool = True,
) -> pd.DataFrame:
    """Find all possible combinations of huts for multiple days."""
    col_names, trip_options = [], pd.DataFrame()
    for i, current_date in enumerate(date_list):
        # collect column names for sorting them in the end
        col_names.extend([f"day{i}", f"name_day{i}", f"places_day{i}"])

        # filter for availability on this date
        avail_current_day = avail_per_date[[current_date]].dropna().rename({current_date: f"places_day{i}"}, axis=1)
        # print(f"Avail on day {i}: {len(avail_current_day)}")

        avail_current_day[f"name_day{i}"] = id_to_hut

        # for last hut: special case, just filter availability, then stop
        if i == len(date_list) - 1:
            trip_options = trip_options.merge(avail_current_day, how="inner", left_on=f"day{i}", right_index=True)
            break

        # check what options we have in general to go to the next hut
        options_to_next_day = avail_current_day.merge(
            feasible_connections, how="inner", left_index=True, right_index=True
        ).reset_index(names=f"day{i}")

        # print(f"Options for transfer from {i} to {i+1}: {len(options_to_next_day)}")

        # merge with overall result
        if i == 0:
            trip_options = options_to_next_day
        else:
            trip_options = options_to_next_day.merge(trip_options, left_on=f"day{i}", right_on=f"day{i}", how="inner")

        # rename columns
        trip_options.rename({"id_target": f"day{i+1}", "distance": f"distance_day{i+1}"}, axis=1, inplace=True)
        col_names.append(f"distance_day{i+1}")
        # print(f"Total options after day {i}: {len(trip_options)}")
    trip_options = trip_options[col_names]

    if require_unique_huts:
        trip_options = trip_options[
            trip_options[[c for c in col_names if c.startswith("day")]].nunique(axis=1) == len(date_list)
        ]

    return trip_options


def generate_date_range(start_date_str: str, end_date_str: str) -> list[str]:
    """Generate all dates between a start and end date."""
    # Define the format

    # Parse the dates
    start_date = datetime.strptime(start_date_str, DATE_FORMAT_IN)
    end_date = datetime.strptime(end_date_str, DATE_FORMAT_IN)

    # Generate the range
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime(DATE_FORMAT_OUT))
        current_date += timedelta(days=1)

    return date_list
