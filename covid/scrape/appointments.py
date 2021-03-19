import json
import logging
from pathlib import Path
from dateutil.parser import parse
from dateutil.parser._parser import ParserError

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

APPOINTMENT_URL = r"https://www.cvs.com/immunizations/covid-19-vaccine?icid" \
                   "=cvs-home-hero1-link2-coronavirus-vaccine"
TIMEOUT = 10
TIMEZONE_JSON = Path(Path(__file__).parent.parent.parent, 'data', 'json',
                     'timezone.json')

class AppointmentScraper:
    def __init__(self, driver, state):
        self.driver = driver
        #self.state_name = state
        self.state_element = state
        self.vaccine_info = 'vaccineinfo-CA' # todo: json of state abbr
        self.city_status_table = 'CA'
        try:
            with open(TIMEZONE_JSON) as json_file:
                self.tz_info = json.load(json_file)
        except FileNotFoundError as err:
            logging.warning(err)
            self.tz_info = {}

    @property
    def state_element(self):
        return self._state_element

    @state_element.setter
    def state_element(self, state):
        logging.debug('Get URL: %s', APPOINTMENT_URL)
        self.driver.get(APPOINTMENT_URL)     
        try:
            state_link = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "a[data-analytics-name={}]".format(state))))
            logging.debug('Found state: %s', state_link.text)
            self._state_element = state_link
        except TimeoutException as exc:
            logging.warning(exc)
            return None

    def click_state_element(self):
        assert self.state_element is not None
        self.driver.execute_script('arguments[0].click();', self.state_element)
    
    @property
    def vaccine_info(self):
        return self._vaccine_info

    @vaccine_info.setter
    def vaccine_info(self, element_id):
        try:
            popup_window = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, element_id)))
            logging.debug('Found popup window: %s',
                          popup_window.get_attribute('id'))
            self._vaccine_info = popup_window
        except TimeoutException as exc:
            logging.warning(exc)
            self._vaccine_info = None
   
    @property
    def city_status_table(self):
        return self._city_status_table

    @city_status_table.setter
    def city_status_table(self, state):
        assert self.vaccine_info is not None
        try:
            table_class = WebDriverWait(self.vaccine_info, TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'covid-status.tableFixHead')))
            logging.debug('Found table: %s',
                          table_class.get_attribute('data-url'))
            table = table_class.find_element_by_tag_name('table')
            self._city_status_table = table.find_element_by_tag_name('tbody')
        except TimeoutException:
            logging.warning('TimeoutException occurred when locating vaccine ' \
                            'status table.')
            self._city_status_table = None

    def raw_timestamp(self):
        assert self.vaccine_info is not None
        try:
            timestamp = WebDriverWait(self.vaccine_info, TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[data-id='timestamp'")))
            logging.debug('Found timestamp: %s',
                          timestamp.get_attribute('data-id'))
            if not timestamp.is_displayed():
                self.click_state_element()
                timestamp = self.vaccine_info.find_element_by_css_selector(
                    "div[data-id='timestamp']")
            return timestamp
        except TimeoutException as exc:
            logging.warning(exc)
            return None
   
    def formatted_timestamp(self):
        try:
            return parse((' ').join(self.raw_timestamp().text.split()[3:6]),
                         tzinfos=self.tz_info)
        except (ParserError, TypeError) as err:
            # raw timestamp was empty
            logging.warning(err)
            return None

    def city_status_entries(self, timestamp):
        assert self.city_status_table is not None
        if not self.city_status_table.is_displayed():
            self.click_state_element()
        entries = []

        for row in self.city_status_table.find_elements_by_tag_name('tr'):
            city = row.find_elements_by_tag_name('td')[0] \
                      .find_element_by_class_name('city').text
            status = row.find_elements_by_tag_name('td')[1] \
                        .find_element_by_class_name('status').text
            entries.append({
                'city': city.split(',')[0],
                'status': status,
                'timestamp': timestamp})
        return entries
