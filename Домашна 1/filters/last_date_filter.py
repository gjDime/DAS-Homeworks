import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import csv


def download_10years(issuer):
    date = datetime.today()
    df_temp = pd.DataFrame()
    for i in range(10):
        to_date = date.strftime('%m/%d/%Y')
        from_date = (date - timedelta(days=365)).strftime('%m/%d/%Y')

        df = download_year(from_date, to_date, issuer)
        df_temp = pd.concat([df_temp, df], ignore_index=True)
        date = date - timedelta(days=365)
    return df_temp


def download_year(from_date, to_date, issuer):
    url = 'https://www.mse.mk/en/stats/symbolhistory/' + issuer
    driver = webdriver.Firefox()
    driver.get(url)

    from_date_input = driver.find_element(By.CSS_SELECTOR, '#FromDate')
    to_date_input = driver.find_element(By.CSS_SELECTOR, '#ToDate')
    button_find = driver.find_element(By.CSS_SELECTOR, '#report-filter-container > ul > li.container-end > input')

    from_date_input.clear()
    from_date_input.send_keys(from_date)

    to_date_input.clear()
    to_date_input.send_keys(to_date)

    button_find.click()
    print(from_date)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#resultsTable')))

    table = driver.find_element(By.CSS_SELECTOR, '#resultsTable')

    headers = []
    thead = table.find_element(By.CSS_SELECTOR, 'thead')  # Re-locate the 'thead'
    for th in thead.find_elements(By.CSS_SELECTOR, 'th'):  # Find all 'th' elements in the 'thead'
        headers.append(th.text.strip())

    # Extract table rows (re-locate the tbody and tr elements)
    rows = []
    tbody = table.find_element(By.CSS_SELECTOR, 'tbody')  # Re-locate the 'tbody'
    for tr in tbody.find_elements(By.CSS_SELECTOR, 'tr'):  # Find all 'tr' elements in the 'tbody'
        row = []
        for td in tr.find_elements(By.CSS_SELECTOR, 'td'):  # Find all 'td' elements in each row
            row.append(td.text.strip())
        rows.append(row)

    df = pd.DataFrame(rows, columns=headers)
    df['Issuer'] = issuer
    driver.quit()
    return df


def tacna_funkcija(listIssuers):
    dataframe = pd.read_csv('stock_market.csv')
    last_column = dataframe.columns[-1]

    last_date_dict = {}
    df_temp = pd.DataFrame()
    for issuer in listIssuers:
        issuer_df = dataframe[dataframe[last_column] == issuer]

        if len(issuer_df) == 0:
            issuer_df = download_10years(issuer)

        df_temp = pd.concat([df_temp, issuer_df], ignore_index=True)

        last_date = issuer_df.iloc[0, 1]
        last_date_dict[issuer] = last_date

    df_temp.to_csv('stock_market.csv')
    return last_date_dict
