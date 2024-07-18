"""This file is for demonstration purposes and will be removed (or replaced by a proper test class)."""

import datetime
import os

import geopandas as gpd
import pandas as pd

from check_availability import AvailabilityChecker
from filtering import filter_huts

if __name__ == "__main__":
    huts = gpd.read_file(os.path.join("data", "huts_database.geojson"))

    # parameters for filtering
    # start from munich
    start_lat, start_lon = 48.1381528, 11.5762854
    # min 100 because munich is boooring and maximal 150 km
    min_distance = 100
    max_distance = 120
    min_altitude = 2000

    # filter huts
    filtered = filter_huts(
        huts,
        min_altitude=min_altitude,
        start_lat=start_lat,
        start_lon=start_lon,
        max_distance=max_distance,
        min_distance=min_distance,
    )
    print("number of huts after filtering", len(filtered))

    # check availability for the top 5
    top_5_rows = filtered.sort_values("distance").head()
    print(top_5_rows)

    # parameters for availability
    start_date = datetime.datetime(2024, 8, 22)
    num_weeks_to_process = 1

    checker = AvailabilityChecker()

    all_avail = []
    for _, row in top_5_rows.iterrows():
        hut_name = row["name"]
        hut_id = row["id"]

        out_df = checker(hut_id, start_date, biweeks_ahead=num_weeks_to_process)
        if len(out_df) > 0:
            out_df.index.name = "room_type"
            out_df.reset_index(inplace=True)
            out_df["hut_name"] = hut_name
        # # uncomment to save hut results as separate files
        # out_df.to_csv(f"outputs_new/{hut_id}.csv")
        all_avail.append(out_df)
    all_avail = pd.concat(all_avail)
    all_avail.to_csv(os.path.join("data", "demo_result.csv"))
    checker.close()
