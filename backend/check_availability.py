"""Scrapes alpsonline.org for availability."""

import datetime
import logging
import os
from typing import Any, Text

import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://www.hut-reservation.org/reservation/book-hut/"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

SERVICE = Service(CHROMEDRIVER_PATH) if os.path.exists(CHROMEDRIVER_PATH) else None

# set up logger
logger = logging.getLogger(__name__)


class AvailabilityChecker:
    """AvailabilityChecker handles scraping alpsonline.org and parsing results into Pandas DataFrames."""

    def __init__(self, base_url: Text = BASE_URL) -> None:
        """Initialize driver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")  # Required for some Linux environments
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument("--remote-debugging-port=9222")  # Set a port for remote debugging
        self.driver = webdriver.Chrome(service=SERVICE, options=chrome_options)
        self.base_url = base_url
        self.wait = WebDriverWait(self.driver, 3)

    def __call__(self, hut_id: int, start_date: datetime.date, end_date: datetime.date) -> dict:
        """
        Callable function of AvailabilityChecker that performs scraping.

        Args:
            hut_id: hut id that is used to check BASE_URL + hut_id
            start_date: start date of query
            end_date: end date of query

        Returns:
            pd.DataFrame containing availability info
            status (whether the request was successful)
        """
        # get url for this hut
        url = self.base_url + str(hut_id) + "/wizard"
        self.driver.get(url)

        # initialize prev table
        old_table_html = ""

        # read preamble
        preamble = self.get_preamble()
        # check if there is a start date in the preamble
        date_from_msg = self.convert_message_to_date(preamble)

        # set start date
        if date_from_msg is not None:
            logger.info(f"Set start date based on preamble {date_from_msg.date()}")
            current_start_date = date_from_msg
        else:
            current_start_date = start_date

        avail_on_date = {}
        # biweek_counter = 0
        attempt_count = 0

        while current_start_date < end_date:
            # get str start and end to paste into calendar
            str_start_date = current_start_date.strftime("%d.%m.%Y")
            str_end_date = (current_start_date + datetime.timedelta(days=14)).strftime("%d.%m.%Y")

            logger.info(f"Hut {hut_id}: {str_start_date} - {str_end_date}")

            # Wait until we find a web element where the date can be input
            try:
                date_input = self.wait.until(EC.visibility_of_element_located((By.ID, "cy-arrivalDate__input")))
            except TimeoutException:
                logger.info("Hut not found (no calendar), break")
                return None, "Error: Not in system!"

            # input start date
            date_input.clear()
            date_input.send_keys(str_start_date)
            date_input.send_keys(Keys.RETURN)

            # input end date
            date_input_end = self.driver.find_element(By.XPATH, "//input[@formcontrolname='departureDate']")
            date_input_end.clear()
            date_input_end.send_keys(str_end_date)
            date_input.send_keys(Keys.RETURN)

            # Load table
            try:
                self.wait_for_table_exists()
            except TimeoutException:
                logger.info("Table does not load")
                try:
                    error_element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "app-error-messages .error_message"))
                    )
                    # put error message into fields
                    for date_index in range(14):
                        current_date = (current_start_date + datetime.timedelta(days=date_index)).strftime("%d.%m.%Y")
                        avail_on_date[current_date] = error_element.text

                    logger.info(f"Error message: {error_element.text}")

                    # try to find a new start date in the error message
                    alternative_start_date = self.convert_message_to_date(error_element.text)
                    if alternative_start_date is not None:
                        # clear and set date
                        self.clear_input_field(date_input)
                        self.clear_input_field(date_input_end)
                        if alternative_start_date == current_start_date:
                            # same error esage as before! --> go a bit further
                            alternative_start_date = alternative_start_date + datetime.timedelta(days=3)
                        # set the start date to the date in the message + 1 (because usually "closed until" msg)
                        current_start_date = alternative_start_date + datetime.timedelta(days=1)
                        logger.info(f"Using error message, set start date to {alternative_start_date}")
                        continue
                except TimeoutException:
                    # no error message show --> error message to unknown
                    for date_index in range(14):
                        current_date = (current_start_date + datetime.timedelta(days=date_index)).strftime("%d.%m.%Y")
                        avail_on_date[current_date] = "Unknown error"

                # clear date
                self.clear_input_field(date_input)
                self.clear_input_field(date_input_end)

                # Try again (two attempts in total, in the first one, just try the same date again)
                if attempt_count == 0:
                    # try second time because sometimes issue that doesn't load directly
                    attempt_count += 1
                else:
                    # After the first attempt, always increase by factor of 3
                    current_start_date += datetime.timedelta(days=3 ** (attempt_count - 1))
                    logger.info(f"Checking {3 ** (attempt_count - 1)} days further")
                    attempt_count += 1
                continue

            # Table was found!
            # Wait for the table content to change
            self.wait_for_table_update(old_table_html)

            table_html = self.driver.find_element(
                By.CSS_SELECTOR, 'table[aria-label="Date Availability Table"]'
            ).get_attribute("outerHTML")

            # Parse the table HTML using BeautifulSoup
            soup = BeautifulSoup(table_html, "html.parser")
            # Find all rows in the table
            rows = soup.find_all("mat-row", class_="mat-mdc-row")
            # Extract data from each row
            for row in rows:
                # Extract date and available seats
                date_cell = row.find("td", class_="table_row_date")
                places_cell = row.find("td", class_="table_row_places")

                if date_cell and places_cell:
                    date = date_cell.get_text(strip=True)  # Extract and clean the date text
                    places = places_cell.get_text(strip=True)  # Extract and clean the available seats text
                    avail_on_date[date] = places.replace("!", "")
                    logger.info(f"-found availability at {date}: {places}")

            self.clear_input_field(date_input)
            self.clear_input_field(date_input_end)

            # go 14 days further
            current_start_date += datetime.timedelta(days=14)

            # Capture the current table content before waiting for it to change
            old_table_html = self.driver.find_element(
                By.CSS_SELECTOR, 'table[aria-label="Date Availability Table"]'
            ).get_attribute("outerHTML")

        return avail_on_date, "Success"

    def wait_for_table_update(self, old_html: Any):
        """Wait until the table content changes compared to the previous iteration."""
        # Wait until the table content changes compared to the previous iteration
        self.wait.until(
            lambda x: self.driver.find_element(
                By.CSS_SELECTOR, 'table[aria-label="Date Availability Table"]'
            ).get_attribute("outerHTML")
            != old_html
        )

    def wait_for_table_exists(self):
        """Wait until the table is present in the DOM."""
        # Wait for the table to update based on the new date input
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table[aria-label="Date Availability Table"]'))
        )

    def get_preamble(self):
        """Load preamble text from the page."""
        try:
            # Locate all preamble sections (multiple spans)
            preamble_elements = WebDriverWait(self.driver, 2).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "app-check-availability-step .welcomeMessage"))
            )

            # Concatenate all the text content from the preamble spans
            preamble_text = " ".join([element.text for element in preamble_elements])
            return preamble_text
        except TimeoutException:  # Double check
            return ""

    def convert_message_to_date(self, message: str):
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

    def clear_input_field(self, element: Any):
        """Clears the input field by selecting all text and deleting it."""
        element.send_keys(Keys.CONTROL + "a")  # Select all text (CMD for Mac)
        element.send_keys(Keys.BACKSPACE)  # Delete selected text
