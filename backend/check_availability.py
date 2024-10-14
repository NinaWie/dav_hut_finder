"""Scrapes alpsonline.org for availability."""

import datetime
import os
from collections import defaultdict
from typing import Any, List, Text

import geopandas as gpd
import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://www.alpsonline.org/reservation/calendar?hut_id="
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

SERVICE = Service(CHROMEDRIVER_PATH) if os.path.exists(CHROMEDRIVER_PATH) else None


class AvailabilityChecker:
    """AvailabilityChecker handles scraping alpsonline.org and parsing results into Pandas DataFrames."""

    def __init__(self, base_url: Text = BASE_URL) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")  # Required for some Linux environments
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument("--remote-debugging-port=9222")  # Set a port for remote debugging
        self.driver = webdriver.Chrome(service=SERVICE, options=chrome_options)
        self.time_to_sleep = 5
        self.base_url = base_url

    def __call__(self, hut_id: int, start_date: datetime.date, biweeks_ahead: int = 1) -> pd.DataFrame:
        """
        Callable function of AvailabilityChecker that performs scraping.

        Args:
            hut_id: hut id that is used to check BASE_URL + hut_id
            start_date: start date of query
            biweeks_ahead: how many weeks to look ahead

        Returns:
            pd.DataFrame containing availability info
        """
        url = self.base_url + str(hut_id)

        # check if hut is in booking system
        reservation_avail = self.check_reservation_possible(url)
        if not reservation_avail:
            print(f"Skipping hut {hut_id} because not part of online reservation system")
            return pd.DataFrame()

        # initialize interactive driver
        self.driver.get(url)

        # repeat x times (usually just one time, which gives two weeks availability)
        date_range_result = []
        for i in range(biweeks_ahead):
            date = start_date + datetime.timedelta(days=14 * i)
            input_date = date.strftime("%d.%m.%Y")
            soup = self.get_soup_for_date(input_date)  # date_input from driver
            # get rooms
            rooms = self.get_rooms(soup)

            # get skip dates
            booking_closed = soup.find_all("div", id=lambda x: x and "bookingClosed" in x)
            skip_dates = [int(r.get("id")[13:]) for r in booking_closed if "display: none" not in r.get("style")]

            # make list of 14 dates (14 max)
            date_list = [date + datetime.timedelta(days=i) for i in range(14)]

            date_cat = self.extract_rooms_from_soup(rooms, date_list, skip_dates)

            date_range_result.append(date_cat)

        # combine the weeks
        date_range_result = pd.concat(date_range_result).swapaxes(1, 0)
        return date_range_result

    def check_reservation_possible(self, url: Text) -> bool:
        """
        Check if the hut is even part of the reservation system.

        Args:
            url: url to check

        Returns:
            bool: True if reservation possible, False if not
        """
        response = requests.get(url)
        if response.status_code != 200:
            return False
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")  # , "lxml")
        rooms = soup.find_all("div", id=lambda x: x and x.startswith("room"))
        return len(rooms) >= 2

    def close(self):
        """Close chrome diver connection."""
        self.driver.quit()

    def get_soup_for_date(self, input_date: datetime.time) -> BeautifulSoup:
        """
        Create BeautifulSoup object for HTML with date entered.

        Args:
            input_date: date to enter in input fields

        Returns:
            soup: BeautifulSoup
        """
        # print("running soup for input date", input_date)
        wait = WebDriverWait(self.driver, 7)
        date_input = wait.until(EC.visibility_of_element_located((By.ID, "fromDate")))
        initial_text = self.driver.find_element(By.ID, "bookingDate0").text

        # Clear the date field and input new date
        date_input.clear()
        date_input.send_keys(input_date)
        date_input.send_keys(Keys.RETURN)
        # time.sleep(self.time_to_sleep)

        # Wait until the text changes, indicating that new data has loaded
        try:
            wait.until(lambda driver: driver.find_element(By.ID, "bookingDate0").text != initial_text)
        except TimeoutException:
            print("Warning: Timed out waiting for text to change")

        # convert to soup
        html_content = self.driver.page_source
        soup = BeautifulSoup(html_content)
        return soup

    def day_id_from_room(self, room: Any) -> int:
        """
        Extract day ID from room soup result.

        Args:
            room (bs Result): beautiful soup result for one room

        Returns:
            int: ID of the day
        """
        room_id = room.get("id")
        return int(room_id.split("-")[0][4:])

    def extract_rooms_from_soup(
        self, rooms: ResultSet, date_list: List[datetime.time], skip_dates: List[int]
    ) -> pd.DataFrame:
        """
        Extract available rooms from bf4.element.ResultSet.

        Args:
            rooms: List containing results from BeautifulSoup scrape
            date_list: List of dates to consider
            skip_dates: List of dates to skip

        Returns:
            date_cat: pd.DataFrame containing available rooms
        """
        day_list = defaultdict(dict)
        cat = "reservation_possible"
        for i in range(len(rooms)):
            room = rooms[i]
            day = self.day_id_from_room(room)
            day_str = date_list[day].strftime("%d.%m.%Y")
            if day in skip_dates:
                day_list[day_str][cat] = ""
            # get category
            cat = room.find("label", id=lambda x: x and x.startswith("bedCategoryLabel")).text.strip()
            free_spaces = room.find("label", id=lambda x: x and x.startswith("freePlaces")).text.strip()
            day_list[day_str][cat] = free_spaces
        date_cat = pd.DataFrame(day_list).swapaxes(1, 0)

        return date_cat

    def get_rooms(self, soup: BeautifulSoup) -> ResultSet:
        """
        Extract room information from BeautifulSoup Object.

        Args:
            soup: BeautifulSoup object containing html data
        Returns:
            bs4.element.ResultSet (actually list) containing rooms information
        """

        return soup.find_all("div", id=lambda x: x and x.startswith("room") and "Info" not in x)

    def availability_specific_date(self, filtered_huts: gpd.GeoDataFrame, check_date: Text) -> pd.DataFrame:
        """
        Runs availabiltiy check for a hut and returns the results for a single day.

        Args:
            filtered_huts: GeoDataFrame containing results of hut filtering
            check_date: date to check

        Returns:
            result: pd.DataFrame encoding availability
        """
        # convert date into datetime object
        date_object = datetime.datetime.strptime(check_date, "%d.%m.%Y")

        # iterate over filtered huts and run availability check
        all_avail = []
        # iterate over all filtered huts
        for _, row in filtered_huts.iterrows():
            hut_name = row["name"]
            hut_id = row["id"]

            out_df = self(hut_id, date_object)
            if len(out_df) > 0:
                out_df.index.name = "room_type"
                out_df.reset_index(inplace=True)
                out_df["hut_name"] = hut_name
            # # uncomment to save hut results as separate files
            # out_df.to_csv(f"outputs_new/{hut_id}.csv")
            all_avail.append(out_df)
        all_avail = pd.concat(all_avail)

        # get only the relevant rows
        result = all_avail[["hut_name", "room_type", check_date]].dropna()
        # transform nr spaces to int
        result[check_date] = result[check_date].apply(lambda x: int(x.split(" ")[0]))
        # rename col
        result = result.rename({check_date: "available_beds"}, axis=1)
        return result
