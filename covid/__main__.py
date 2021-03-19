import sys
import argparse
import configparser
import logging
import logging.config
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError
from selenium import webdriver

from .scrape.appointments import AppointmentScraper
from .fill.schedule import AppointmentScheduler
from .notify.msg import email, text

AVAILABILITY_CSV = Path(Path(__file__).parent.parent, 'data', 'csv',
                        'historical_availability.csv')

class SysArgFilter(logging.Filter):
    def __init__(self):
        self.sysarg = '{{{}}}'.format(' '.join(sys.argv[1:]))

    def filter(self, record):
        record.sysarg = self.sysarg
        return True


def main():
    # set up logging
    log_dir = Path(Path(__file__).parent.parent, 'log')
    logging_webdriver_path = Path(log_dir, 'geckodriver.log')
    logging_config_path = Path(log_dir, 'config.ini')
    logging.config.fileConfig(logging_config_path)
    logging.getLogger().addFilter(SysArgFilter())
    
    # set up webdriver
    options = webdriver.FirefoxOptions()
    options.headless = True
    """
    driver = webdriver.Firefox(options=options,
                               service_log_path=logging_webdriver_path)
    """

    with webdriver.Firefox(options=options,
                           service_log_path=logging_webdriver_path) as driver:
        logging.debug('Initialized webdriver.')
        if args.find:
            scraper = AppointmentScraper(driver, 'California')
            timestamp = scraper.formatted_timestamp()
            entries = scraper.city_status_entries(timestamp)
            
            if not AVAILABILITY_CSV.exists():
                logging.debug("File '{}' not found. Creating file..." \
                              .format(AVAILABILITY_CSV))
                AVAILABILITY_CSV.touch()
            try:
                df = pd.read_csv(AVAILABILITY_CSV)
            except EmptyDataError:
                df = pd.DataFrame()
            finally:
                df = df.append(entries, ignore_index=True)
            
            city_filter = (((df.city=='San Jose') | (df.city=='Santa Clara') |
                            (df.city=='Campbell') | (df.city=='Los Gatos'))
                           & (df.timestamp==timestamp))
            if args.verbose:
                print(df[city_filter])
            if args.notify:
                df_avail = df[city_filter & (df.status=='Available')]
                if not df_avail.empty:
                    cities = (', ').join(df_avail.city.values)
                    msg = "Vaccines available in the following cities: " + cities
                    email(msg)
                    text(msg)
            if args.archive:
                logging.debug('Appending latest vaccine availability to csv...')
                df.to_csv(AVAILABILITY_CSV, index=False)
            if args.schedule:
                scheduler = AppointmentScheduler()
                """
                driver.get(BASE_URL)
                fill_questionnaire(driver)
                fill_vaccination_type(driver)
                determine_eligibility(driver)
                confirm_eligibility(driver)
                start_scheduling(driver)
                schedule_dose(driver)
                """
    #driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find and/or schedule a ' \
                                     'COVID vaccine appointment.')
    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        default=False,
                        help='Print output to console')
    parser.add_argument('-f',
                        '--find',
                        action='store_true',
                        default=False,
                        help='Find available vaccine appointments')
    parser.add_argument('-s',
                        '--schedule',
                        action='store_true',
                        default=False,
                        help='Schedule a vaccine appointment')
    parser.add_argument('-n',
                        '--notify',
                        action='store_true',
                        default=False,
                        help='Send an email or text upon finding an ' \
                        'available appointment')
    parser.add_argument('-a',
                        '--archive',
                        action='store_true',
                        default=False,
                        help='Archive historical vaccine availability')
    args = parser.parse_args()
    main()
