from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

from filters.last_date_filter import download_data


def update(last_date_dict):
    today = datetime.today().strftime('%m-%d-%Y').replace('-', '/')

    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    updated_data = []
    for issuer in last_date_dict.keys():
        if last_date_dict[issuer] != today:
            update_df = download_updates(last_date_dict[issuer], today, issuer, driver)
            if not update_df.empty:
                updated_data.append(update_df)

    if updated_data:
        csv = pd.read_csv('stock_market.csv')
        updated_data.append(csv)
        updated_df = pd.concat(updated_data, ignore_index=True)
        updated_df.sort_values(by='Issuer', ascending=True, inplace=True)
        updated_df.to_csv('stock_market.csv', index=False)

    driver.quit()

    print('Updated')


def download_updates(issuer, from_date, to_date, driver):
    driver.get('https://www.mse.mk/en/stats/symbolhistory/' + issuer)

    df = download_data(from_date, to_date, issuer, driver)

    if not df.empty:
        print(issuer)
    return df

    # print(from_date, to_date)

