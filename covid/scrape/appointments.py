import json
from pathlib import Path
from dateutil.parser import parse
from dateutil.parser._parser import ParserError

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

APPOINTMENT_URL = r"https://www.cvs.com/immunizations/covid-19-vaccine?icid=cvs-home-hero1-link2-coronavirus-vaccine"
TIMEOUT = 10
TIMEZONE_JSON = Path(Path(__file__).parent.parent.parent, 'data', 'json', 'timezone.json')

class AppointmentScraper:
    def __init__(self, driver, state):
        self.driver = driver
        self.state_name = state
        self.state_element = None
        self.timestamp = None
        try:
            with open(TIMEZONE_JSON) as json_file:
                self.tz_info = json.load(json_file)
        except FileNotFoundError:
            # timezone.json missing
            self.tz_info = {}

    """Return list of web elements corresponding to all states/territories."""
    def get_states(self):
        self.driver.get(APPOINTMENT_URL)     
        try:
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'type__link__text.modal--link.modal--cta')))
        except TimeoutException:
            print("Timeout...")
            return None
        return self.driver.find_elements_by_class_name('type__link__text.modal--link.modal--cta')

    def get_state_by_name(self):
        for state in self.get_states():
            if state.find_element_by_class_name('link__text').text.lower() == self.state_name.lower():
                #print("Found state: ", state.find_element_by_class_name('link__text').text)
                return state

        return None

    def get_vaccine_info(self):
        assert self.state_element is not None
        self.driver.execute_script('arguments[0].click();', self.state_element)
        try:
            #return WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, 'vaccineinfo-CA')))
            return WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'modal__box.modal--active')))
        except TimeoutException:
            print("Timeout...")
            return None

    def get_city_status_table(self):
        try:
            return WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[13]/div/div/div/div/div/div[1]' \
                                                '/div[2]/div/div/div[2]/div/div[6]/div/div/table/tbody')))
        except TimeoutException:
            print("Timeout...")
            return None

    def get_raw_timestamp(self):
        try:
            return WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[13]/div/div/div/div/div/div[1]' \
                                                '/div[2]/div/div/div[2]/div/div[5]/div'))).text.split()[3:6] 
        except TimeoutException:
            print("Timeout...")
            return None

    def get_formatted_timestamp(self):
        try:
            return parse((' ').join(self.get_raw_timestamp()), tzinfos=self.tz_info)
        except ParserError:
            # raw timestamp was empty
            return None

    def get_city_status_entries(self):
        self.state_element = self.get_state_by_name()
        self.get_vaccine_info()     
        self.timestamp = self.get_formatted_timestamp()
        table = self.get_city_status_table()
        entries = []
        
        for row in table.find_elements_by_tag_name('tr'):
            city = row.find_elements_by_tag_name('td')[0].find_element_by_class_name('city').text
            status = row.find_elements_by_tag_name('td')[1].find_element_by_class_name('status').text
            #print("City: {}\tStatus: {}".format(city.split(',')[0], status))
            entries.append({'city': city.split(',')[0], 'status': status, 'timestamp': self.timestamp})
        return entries
