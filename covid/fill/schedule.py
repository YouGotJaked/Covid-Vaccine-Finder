from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

BASE_URL = r"https://www.cvs.com/vaccine/intake/store/covid-screener/covid-qns"
QUESTIONNAIRE_JSON = Path(Path(__file__).parent.parent.parent, 'data', 'json',
                          'questionnaire.json')

class AppointmentScheduler:
    def __init__(self, driver):
        self.driver = driver
        try:
            with open(QUESTIONNAIRE_JSON) as json_file:
                self.questionnaire = json.load(json_file)
        except FileNotFoundError:
            # need to fill in demographic data
            self.questionnaire = {}

    def ip_blocked(self):
        return self.driver.current_url.contains('/vaccine/intake/error')

    def click_continue(self):
        footer = self.driver.find_element_by_class_name('footer-content-wrapper')
        btn_continue = footer.find_element_by_class_name('btn-control')
        self.driver.execute_script('arguments[0].click();', btn_continue)

    def fill_questionnaire(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'q7_2')))
        except TimeoutException:
            print("Timeout...")
            return
        
        questions = [self.driver.find_element_by_id('q7_2'),
                     self.driver.find_element_by_id('q8_2'),
                     self.driver.find_element_by_id('q9_2')]
        # fill questionnaire
        for q in questions:
            self.driver.execute_script('arguments[0].click();', q)

        # continue
        self.click_continue()

    def fill_vaccination_type(self): 
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'customRadio_1')))
        except TimeoutException:
            print("Timeout...")
            return

        btn_start_vaccination = self.driver.find_element_by_id('customRadio_1')
        self.driver.execute_script('arguments[0].click();', btn_start_vaccination)

        # continue
        self.click_continue()

    def determine_eligibility(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'jurisdiction')))
        except TimeoutException:
            print("Timeout...")
            return

        select = Select(self.driver.find_element_by_id('jurisdiction'))
        select.select_by_visible_text('California')

        # continue
        self.click_continue()

    def confirm_eligibility(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'q20')))
        except TimeoutException:
            print("Timeout...")
            return

        form_age = self.driver.find_element_by_id('q1_0')
        form_age.send_keys(AGE)

        btn_group = self.driver.find_element_by_id('q20')
        self.driver.execute_script('arguments[0].click();', btn_group)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'qlist')))
        except TimeoutException:
            print("Timeout...")
            return

        select = Select(self.driver.find_element_by_id('qlist'))
        select.select_by_visible_text('Teachers K-12, Daycare and preschool workers, and staff members')

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'qtext')))
        except TimeoutException:
            print("Timeout...")
            return

        form_employer = self.driver.find_element_by_id('qtext')
        form_employer.send_keys(EMPLOYER)

        btn_consent = self.driver.find_elemeny_by_id('consentText')
        driver.execute_script('arguments[0].click();', btn_consent)

        # continue
        self.click_continue()

    def start_scheduling(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS, 'footer-content-wrapper')))
        except TimeoutException:
            print("Timeout...")
            return

        self.click_continue()

    def schedule_dose(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'address')))
        except TimeoutException:
            print("Timeout...")
            return

        form_address = self.driver.find_elemeny_by_id('address')
        form_address.send_keys(ZIP)

        btn_search = self.driver.find_element_by_class_name('search-icon flex-button-search')
        self.driver.execute_script('arguments[0].click();', btn_search)
