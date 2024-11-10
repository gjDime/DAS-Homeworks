from datetime import datetime

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC


def update(last_date_dict):
    today = datetime.today().strftime('%m-%d-%Y')
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    for issuer in last_date_dict.keys():
        if last_date_dict[issuer] != today:
            updated_df = download_updates(issuer, last_date_dict[issuer], today, driver)
            updated_df.to_csv('stock_market.csv', mode='a', header=False, index=False)

    driver.quit()
    csv = pd.read_csv('stock_market.csv')
    csv = csv.sort_values(by=['Issuer'], ascending=True)
    csv.to_csv('stock_market.csv', index=False)


def download_updates(issuer, last_date, today, driver):
    driver.get('https://www.mse.mk/en/stats/symbolhistory/' + issuer)
    to_date = today
    from_date = last_date.strftime('%m/%d/%Y')

    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#FromDate')))
    from_date_input = driver.find_element(By.CSS_SELECTOR, '#FromDate')
    from_date_input.clear()
    from_date_input.send_keys(from_date)

    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ToDate')))
    to_date_input = driver.find_element(By.CSS_SELECTOR, '#ToDate')
    to_date_input.clear()
    to_date_input.send_keys(to_date)

    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.btn')))
    # button_find = driver.find_element(By.CSS_SELECTOR, '#report-filter-container > ul > li.container-end > input')
    button_find = driver.find_element(By.CSS_SELECTOR, 'input.btn')
    button_find.click()

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#resultsTable')))
    table = driver.find_element(By.CSS_SELECTOR, '#resultsTable')

    rows = []
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    for tr in tbody.find_elements(By.TAG_NAME, 'tr'):
        row = []
        for td in tr.find_elements(By.TAG_NAME, 'td'):
            row.append(td.text.strip())
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.dropna(subset=['Date'])
    df = df[df['Volume'] != '0']
    df['Issuer'] = issuer
    return df
