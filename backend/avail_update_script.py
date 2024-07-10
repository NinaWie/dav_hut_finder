import time
import os
import json
import datetime
import pandas as pd
import geopandas as gpd
from check_availability import AvailabilityChecker

WEEKS_TO_PROCESS = 12  # checking availability for the next 12 weeks
SAVE_EVERY = 5

if __name__ == "__main__":
    not_in_system = []

    # load huts
    huts = gpd.read_file(os.path.join("data", "huts_database.geojson"))

    # load checker
    checker = AvailabilityChecker()
    # start today
    start_date = datetime.datetime.today()

    tic = time.time()
    all_avail = []
    for i, row in huts.iterrows():
        hut_name = row["name"]
        hut_id = row["id"]
        print("Processing hut", i, hut_id, hut_name)

        out_df = checker(hut_id, start_date, biweeks_ahead=WEEKS_TO_PROCESS // 2)
        if len(out_df) > 0:
            out_df.index.name = "room_type"
            out_df.reset_index(inplace=True)
            out_df["id"] = hut_id
        else:
            not_in_system.append(hut_id)
        # # uncomment to save hut results as separate files
        # out_df.to_csv(f"outputs_new/{hut_id}.csv")
        all_avail.append(out_df)

        if i % SAVE_EVERY == 0:
            pd.concat(all_avail).to_csv(os.path.join("data", "availability.csv"))

            with open(os.path.join("data", "not_avail.json"), "w") as outfile:
                json.dump(not_in_system, outfile)
    print("finished!", time.time() - tic)
