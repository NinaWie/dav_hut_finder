"""Script to check the availability of huts and write to database."""

import datetime
import json
import logging
import os
import sys
import time

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from slack import WebClient
from slack.errors import SlackApiError
from sqlalchemy import create_engine

from check_availability import AvailabilityChecker

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def convert_non_int_to_zero(x: str) -> int:
    """Convert value to integers."""
    try:
        val = int(x)
    except ValueError:
        val = 0
    return val


# db login for database
DB_LOGIN_PATH = "db_login.json"
SKIP_NOT_IN_SYSTEM = True
PATH_NOT_IN_SYSTEM = os.path.join("data", "not_in_system.json")
DAYS_TO_PROCESS = 31 * 8
SAVE_TO_CSV = False
CLIENT = WebClient(token=os.environ["SLACK_TOKEN"])

# Set up database connection
with open(DB_LOGIN_PATH, "r") as infile:
    db_credentials = json.load(infile)


def get_con():
    """Initialize connection to database."""
    return psycopg2.connect(**db_credentials)


# create engine
engine = create_engine("postgresql+psycopg2://", creator=get_con)

# # Create table in database - only run once
# CREATE TABLE hut_availability (
#     hut_id INT NOT NULL,
#     date TEXT NOT NULL,
#     places_avail INT NOT NULL,
#     last_updated TIMESTAMP DEFAULT NOW(),
#     UNIQUE (hut_id, date)
# );


# Insert/update function
def update_hut_availability(hut_data: tuple) -> None:
    """
    Inserts or updates hut availability in the database.

    hut_data is a list of tuples: [(hut_id, date, places_avail), ...]
    """
    query = """
    INSERT INTO hut_availability (hut_id, date, places_avail, last_updated)
    VALUES %s
    ON CONFLICT (hut_id, date)
    DO UPDATE SET
        places_avail = EXCLUDED.places_avail,
        last_updated = CURRENT_DATE;
    """
    try:
        conn = psycopg2.connect(**db_credentials)
        cur = conn.cursor()
        execute_values(cur, query, hut_data)
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Updated {len(hut_data)} records.")
    except Exception as e:
        logger.error(f"Database error: {e}")


def post_to_slack(message: str) -> None:
    """Post message to Slack channel."""
    try:
        CLIENT.chat_postMessage(channel="#hut-finder", text=message, username="PennyMe")
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        raise e


# create driver for scraping
checker = AvailabilityChecker()

# set start and end date
today = datetime.datetime.today()
today_date = today.date()
start_date = today
end_date = today + datetime.timedelta(days=DAYS_TO_PROCESS)

tic_start = time.time()

if os.path.exists(PATH_NOT_IN_SYSTEM):
    with open(PATH_NOT_IN_SYSTEM, "r") as infile:
        huts_not_in_system = json.load(infile)
else:
    huts_not_in_system = []

# result lists
all_avail = []
total_errors, successful_updates = 0, 0

post_to_slack("Starting availability check...")

# iterate over huts
for hut_id in range(1, 673):
    logger.info(f"----------- HUT {hut_id} --------")
    tic = time.time()

    # skip huts that cannot be booked online
    if SKIP_NOT_IN_SYSTEM and hut_id in huts_not_in_system:
        logger.info(f"Not in system - skip hut {hut_id}")
        continue

    # call availability checker
    try:
        # result_for_hut, status = checker(hut_id, start_date, end_date)
        result_for_hut, status = checker.retrieve_from_calendar(hut_id, num_months=DAYS_TO_PROCESS // 31)
    except Exception as e:
        checker.quit()
        del checker
        logger.error(f"Uncaught error! {e}")
        time.sleep(10)  # sleep 10 seconds to recover
        checker = AvailabilityChecker()  # reinitialize checker
        logger.info("Reinstated checker, continuing...")
        total_errors += 1
        if total_errors > 5:
            logger.error("Too many errors, exiting...")
            sys.exit(1)
        continue

    # check if an error was returned
    if status == "Error: Not in system!":
        huts_not_in_system.append(hut_id)
        continue
    elif status != "Success":
        logger.error(f"{hut_id} failed with error {status}")
        continue

    # update the database
    result_for_hut_tuple = [
        (hut_id, date, int(places_avail), today_date)
        for date, places_avail in result_for_hut.items()
        if isinstance(places_avail, int) or places_avail.isdigit()
    ]
    update_hut_availability(result_for_hut_tuple)
    successful_updates += 1

    if hut_id % 10 == 0:
        # Save the huts that are not in system
        with open(os.path.join("data", "not_in_system.json"), "w") as outfile:
            json.dump(huts_not_in_system, outfile)

    if SAVE_TO_CSV:
        # Saving as csv
        # add to dataframe
        result_for_hut_df = pd.DataFrame(result_for_hut, index=[hut_id])
        all_avail.append(result_for_hut_df)

        # Add to availability csv and save
        pd.concat(all_avail).to_csv(os.path.join("availability.csv"))

    logger.info(f"Time for hut {hut_id}: {time.time() - tic}")

logger.info(f"Total runtime {time.time() - tic_start}")
# quit checker
checker.quit()

post_to_slack(
    f"Finished availability check! Total runtime: {time.time() - tic_start:.2f} seconds.\
    \n{len(huts_not_in_system)} huts not in system.\
    \nTotal errors: {total_errors}.\
    \nTotal huts checked: {successful_updates}."
)

# Save the huts that are not in system
with open(os.path.join("data", "not_in_system.json"), "w") as outfile:
    json.dump(huts_not_in_system, outfile)


if SAVE_TO_CSV:
    all_avail = pd.concat(all_avail)
    # sort the dates (previously unsorted)
    final_avail_table = all_avail[
        sorted(
            all_avail.columns,
            key=lambda x: datetime.datetime(int(x.split(".")[2]), int(x.split(".")[1]), int(x.split(".")[0])),
        )
    ]
    # save to csv
    final_avail_table.index.name = "id"
    final_avail_table.to_csv(os.path.join("availability.csv"))

    # transform to int (remove error messages)
    final_avail_int = final_avail_table.applymap(convert_non_int_to_zero).reset_index().sort_values("id")
    final_avail_int.to_csv(os.path.join("availability_int.csv"))
