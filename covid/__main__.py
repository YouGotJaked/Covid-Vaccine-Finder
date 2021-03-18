import argparse
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError
from selenium import webdriver

from .scrape.appointments import AppointmentScraper
from .fill.schedule import AppointmentScheduler
from .notify.msg import email, text

AVAILABILITY_CSV = Path(Path(__file__).parent.parent, 'data', 'csv',
                        'historical_availability.csv')

def main():
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    if args.find:
        scraper = AppointmentScraper(driver, 'California')
        entries = scraper.get_city_status_entries()
        
        if not AVAILABILITY_CSV.exists():
            AVAILABILITY_CSV.touch()
        try:
            df = pd.read_csv(AVAILABILITY_CSV)
        except EmptyDataError:
            df = pd.DataFrame()
        finally:
            df = df.append(entries, ignore_index=True)

        city_filter = (((df.city=='San Jose') | (df.city=='Santa Clara') |
                        (df.city=='Campbell') | (df.city=='Los Gatos'))
                       & (df.timestamp==scraper.timestamp))
        if args.verbose:
            print(df[city_filter])
        if args.notify:
            df_avail = df[city_filter & (df.status=='Available')]
            if not df_avail.empty:
                cities = (', ').join(df_avail.city.values)
                msg = "Vaccines available in the following cities: " + cities
                email(msg)
                text(msg)
        df.to_csv(AVAILABILITY_CSV, index=False)
    elif args.schedule:
        scheduler = AppointmentScheduler()
    driver.quit()
    """
    with webdriver.Firefox(options=options) as driver:
        ca = appointments.get_state_by_name(driver, 'California')
        info = appointments.get_vaccine_info(driver, ca)
        entries = appointments.get_city_status_entries(driver, info)
        if not AVAILABILITY_CSV.exists():
            AVAILABILITY_CSV.touch()
        try:
            df = pd.read_csv(AVAILABILITY_CSV)
        except EmptyDataError:
            df = pd.DataFrame()
        finally:
            df = df.append(entries, ignore_index=True)
            city_filter = (df.city == 'San Jose') | (df.city == 'Santa Clara')
            print(df[city_filter])
            df.to_csv(AVAILABILITY_CSV, index=False)
    """
        
    """
    driver.get(BASE_URL)
    fill_questionnaire(driver)
    fill_vaccination_type(driver)
    determine_eligibility(driver)
    confirm_eligibility(driver)
    start_scheduling(driver)
    schedule_dose(driver)
    """

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
    args = parser.parse_args()
    main()
