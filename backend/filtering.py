"""filtering.py implements functions to filter huts by user input."""

import geopandas as gpd
import numpy as np
import pandas as pd
from haversine import haversine


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
    **kwargs,
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
        min_places: minimum number of huts
        max_places: maximum number of huts
        verbose: verbose debug output
        **kwargs: any other args

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
