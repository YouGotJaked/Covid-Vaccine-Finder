import context
from covid.scrape.appointments import AppointmentScraper
from selenium import webdriver

options=webdriver.FirefoxOptions()
options.headless=True
driver=webdriver.Firefox(options=options)
scraper = AppointmentScraper(driver, 'California')
print('state_element: ', scraper.state_element.text)
print('vaccine_info[class]: ', scraper.vaccine_info.get_attribute('class'))
print('vaccine_info[id]: ', scraper.vaccine_info.get_attribute('id'))
print('raw_ts[data-id]: ', scraper.raw_timestamp().get_attribute('data-id'))
print('raw_ts[class]: ', scraper.raw_timestamp().get_attribute('class'))
print('ts: ', scraper.formatted_timestamp())
print(scraper.city_status_entries(scraper.formatted_timestamp()))
driver.quit()
