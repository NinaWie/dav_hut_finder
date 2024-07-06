import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
import datetime
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

BASE_URL = "https://www.alpsonline.org/reservation/calendar?hut_id="


class AvailabilityChecker:
    def __init__(self, base_url: str = BASE_URL):
        self.driver = webdriver.Chrome()
        self.time_to_sleep = 5
        self.base_url = base_url

    def __call__(self, hut_id, start_date, biweeks_ahead: int = 1):
        # set url to hut
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

    def check_reservation_possible(self, url):
        """Check if the hut is even part of the reservation system"""
        response = requests.get(url)
        if response.status_code != 200:
            return False
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")  # , "lxml")
        rooms = soup.find_all("div", id=lambda x: x and x.startswith("room"))
        if len(rooms) < 2:
            return False
        else:
            return True

    def close(self):
        self.driver.quit()

    def get_soup_for_date(self, input_date):
        # print("running soup for input date", input_date)
        wait = WebDriverWait(self.driver, 10)
        date_input = wait.until(EC.visibility_of_element_located((By.ID, "fromDate")))
        date_input.clear()
        date_input.send_keys(input_date)
        date_input.send_keys(Keys.RETURN)
        time.sleep(self.time_to_sleep)
        # convert to soup
        html_content = self.driver.page_source
        soup = BeautifulSoup(html_content)
        return soup

    def day_id_from_room(self, room):
        room_id = room.get("id")
        return int(room_id.split("-")[0][4:])

    def extract_rooms_from_soup(self, rooms, date_list, skip_dates):
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

    def get_rooms(self, soup):
        return soup.find_all("div", id=lambda x: x and x.startswith("room") and "Info" not in x)
