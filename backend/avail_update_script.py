"""Script to check the availability of huts and write to database."""

import datetime
import os
import time
from typing import Any

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# hut_id = 79
time_to_sleep = 5


def clear_input_field(element: Any):
    """Clears the input field by selecting all text and deleting it."""
    element.send_keys(Keys.CONTROL + "a")  # Select all text (CMD for Mac)
    element.send_keys(Keys.BACKSPACE)  # Delete selected text


BASE_URL = "https://www.hut-reservation.org/reservation/book-hut/"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

SERVICE = Service(CHROMEDRIVER_PATH) if os.path.exists(CHROMEDRIVER_PATH) else None

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")  # Required for some Linux environments
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument("--remote-debugging-port=9222")  # Set a port for remote debugging
driver = webdriver.Chrome(service=SERVICE, options=chrome_options)


def wait_for_table_update(old_html: Any):
    """Wait until the table content changes compared to the previous iteration."""
    # Wait until the table content changes compared to the previous iteration
    wait.until(
        lambda driver: driver.find_element(
            By.CSS_SELECTOR, 'table[aria-label="Date Availability Table"]'
        ).get_attribute("outerHTML")
        != old_html
    )


def wait_for_table_exists():
    """Wait until the table is present in the DOM."""
    # Wait for the table to update based on the new date input
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table[aria-label="Date Availability Table"]')))


def is_error_message_displayed():
    """Check if an error message is displayed on the page."""
    try:
        # Wait briefly to check if the error message appears
        error_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "app-error-messages .error_message"))
        )
        if "Datum liegt außerhalb des möglichen Reservierungszeitraums" in error_element.text:
            return True
        return False
    except TimeoutException:  # Double check
        return False  # No error message found


def get_preamble():
    """Load preamble text from the page."""
    try:
        # Locate all preamble sections (multiple spans)
        preamble_elements = WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "app-check-availability-step .welcomeMessage"))
        )

        # Concatenate all the text content from the preamble spans
        preamble_text = " ".join([element.text for element in preamble_elements])
        return preamble_text
        # Check if "Sommersaisonstart" or similar keywords are present
        # if "Sommersaisonstart" in preamble_text or "Saisonstart" in preamble_text:
        #     print(f"Start date information found: {preamble_text}")
        #     return True
        # else:
        #     print("No start date information in the preamble.")
        #     return False
    except TimeoutException:  # Double check
        return ""


def convert_message_to_date(message: str):
    """Find date in message if possible."""
    try:
        if "Sommersaisonstart" in message:
            hut_open_date = message.split("Sommersaisonstart")[-1]
            dd, mm, yy = hut_open_date.split(".")
            date_from_msg = datetime.datetime(int(yy), int(mm), int(dd))
            return date_from_msg
        elif "geschlossen" in message:
            error_parts = message.split(" ")
            dd, mm, yy = error_parts[-2].split(".")
            date_from_msg = datetime.datetime(int(yy), int(mm), int(dd))
            return date_from_msg
        elif "closed until" in message or "fino al" in message:
            error_parts = message[:-1].split(" ")  # delete dot and divide
            dd, mm, yy = error_parts[-1].split(".")
            date_from_msg = datetime.datetime(int(yy), int(mm), int(dd))
            return date_from_msg
        elif "bewarteten" in message and "unbewarteten" in message:
            for yy in np.arange(2025, 2030, 1):
                str_yy = f".{yy}"
                # iterate over all years to make it work also for the next years
                if str_yy in message:
                    date_part = (message.split(str_yy)[0]).split(" ")[-1]
                    dd, mm = date_part.split(".")
                    date_from_msg = datetime.datetime(int(yy), int(mm), int(dd))
                    return date_from_msg
    except ValueError:
        pass
    return None


fixed_start_date = datetime.datetime.today() + datetime.timedelta(days=60)
fixed_end_date = datetime.datetime.today() + datetime.timedelta(days=200)

old_table_html = ""

huts_not_in_system = []

tic_start = time.time()

all_avail = []
for hut_id in np.arange(478, 673):
    tic = time.time()

    # get url for this hut
    url = BASE_URL + str(hut_id) + "/wizard"
    driver.get(url)

    # read preamble
    preamble = get_preamble()
    # check if there is a start date in the preamble
    date_from_msg = convert_message_to_date(preamble)

    # set start date
    if date_from_msg is not None:
        print("Set start date based on preamble", date_from_msg)
        current_start_date = date_from_msg
    else:
        current_start_date = fixed_start_date

    avail_on_date = {}
    # biweek_counter = 0
    first_attempt = True

    print("-----------")

    while current_start_date < fixed_end_date:
        # date = start_date_check + datetime.timedelta(days=14 * i)
        str_start_date = current_start_date.strftime("%d.%m.%Y")
        str_end_date = (current_start_date + datetime.timedelta(days=14)).strftime("%d.%m.%Y")

        print(hut_id, str_start_date, "-", str_end_date)

        # start date
        wait = WebDriverWait(driver, 3)
        try:
            date_input = wait.until(EC.visibility_of_element_located((By.ID, "cy-arrivalDate__input")))
        except TimeoutException:
            for date_index in range(14):
                current_date = (current_start_date + datetime.timedelta(days=date_index)).strftime("%d.%m.%Y")
                avail_on_date[current_date] = "Hut not found"
                print("Hut not found (no calendar), break")
            huts_not_in_system.append(hut_id)
            break

        date_input.clear()
        date_input.send_keys(str_start_date)
        date_input.send_keys(Keys.RETURN)

        # end date
        date_input_end = driver.find_element(By.XPATH, "//input[@formcontrolname='departureDate']")
        date_input_end.clear()
        date_input_end.send_keys(str_end_date)
        date_input.send_keys(Keys.RETURN)

        # Load table
        try:
            wait_for_table_exists()
        except TimeoutException:
            print("Table does not load")
            try:
                error_element = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "app-error-messages .error_message"))
                )
                # put error message into fields
                for date_index in range(14):
                    current_date = (current_start_date + datetime.timedelta(days=date_index)).strftime("%d.%m.%Y")
                    avail_on_date[current_date] = error_element.text

                print("error message", error_element.text)
                alternative_start_date = convert_message_to_date(error_element.text)
                if alternative_start_date is not None:
                    # clear and set date
                    clear_input_field(date_input)
                    clear_input_field(date_input_end)
                    if alternative_start_date == current_start_date:
                        # same error esage as before! --> go a bit further
                        alternative_start_date = alternative_start_date + datetime.timedelta(days=3)
                    current_start_date = alternative_start_date + datetime.timedelta(days=1)
                    print("Using error message, set start date to", alternative_start_date)
                    continue
            except TimeoutException:  # Double check
                for date_index in range(14):
                    current_date = (current_start_date + datetime.timedelta(days=date_index)).strftime("%d.%m.%Y")
                    avail_on_date[current_date] = "No error"
            # clear and set date
            clear_input_field(date_input)
            clear_input_field(date_input_end)
            # Two attempts: in the first one, just try the same date again.
            if not first_attempt:
                current_start_date += datetime.timedelta(days=3)
                print("Look three days further")
            else:
                first_attempt = False
                print("Try second time")
            continue

        # Wait for the table content to change
        wait_for_table_update(old_table_html)

        table_html = driver.find_element(By.CSS_SELECTOR, 'table[aria-label="Date Availability Table"]').get_attribute(
            "outerHTML"
        )

        # Parse the table HTML using BeautifulSoup
        soup = BeautifulSoup(table_html, "html.parser")
        # Find all rows in the table
        rows = soup.find_all("mat-row", class_="mat-mdc-row")
        # Extract data from each row
        availability = []
        for row in rows:
            # Extract date and available seats
            date_cell = row.find("td", class_="table_row_date")
            places_cell = row.find("td", class_="table_row_places")

            if date_cell and places_cell:
                date = date_cell.get_text(strip=True)  # Extract and clean the date text
                places = places_cell.get_text(strip=True)  # Extract and clean the available seats text
                avail_on_date[date] = places.replace("!", "")
                print("found availability", date, places)

        # Print the extracted availability
        # for entry in availability:
        #     avail_on_date.append(entry["date"]: entry['available_places']
        #     print(f"Date: {entry['date']}, Available Places: {entry['available_places']}")

        # date_input.clear()
        # date_input_end.clear()

        clear_input_field(date_input)
        clear_input_field(date_input_end)

        current_start_date += datetime.timedelta(days=14)

        # Capture the current table content before waiting for it to change
        old_table_html = driver.find_element(
            By.CSS_SELECTOR, 'table[aria-label="Date Availability Table"]'
        ).get_attribute("outerHTML")

    all_avail.append(pd.DataFrame(avail_on_date, index=[hut_id]))

    # Add to availability csv
    pd.concat(all_avail).to_csv(os.path.join("availability_final_part.csv"))

    # with open(os.path.join("data", "not_avail.json"), "w") as outfile:
    #     json.dump(not_in_system, outfile)

    print(f"Total time for hut {hut_id}", time.time() - tic)

all_avail = pd.concat(all_avail)

out = all_avail[
    sorted(
        all_avail.columns,
        key=lambda x: datetime.datetime(int(x.split(".")[2]), int(x.split(".")[1]), int(x.split(".")[0])),
    )
]
out.to_csv(os.path.join("availability_sorted_final_part.csv"))

print("Total total time", time.time() - tic_start)


# import json
# import psycopg2
# with open("/Users/ninawiedemann/Documents/Projects/dav_hut_finder/backend/db_login.json", "r") as infile:
#     db_credentials = json.load(infile)

# from sqlalchemy import create_engine
# def get_con():
#     return psycopg2.connect(**db_credentials)

# engine = create_engine('postgresql+psycopg2://', creator=get_con)
