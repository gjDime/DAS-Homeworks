from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


def update(last_date_dict):
    today = datetime.today().strftime('%m-%d-%Y')

    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    for issuer in last_date_dict.keys():
        if last_date_dict[issuer] != today:
            updated_df = download_updates(issuer, last_date_dict[issuer], today, driver)
            if len(updated_df) > 0:
                updated_df.to_csv('stock_market.csv', mode='a', header=False, index=False)

    driver.quit()
    csv = pd.read_csv('stock_market.csv')
    csv = csv.sort_values(by=['Issuer'], ascending=True)
    csv.to_csv('stock_market.csv', index=False)
    # for col in csv.columns[1:9]:
    #     csv[col] = pd.to_numeric(csv[col], errors='coerce')
    # for col in csv.columns[1:9]:
    #     csv[col] = csv[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "0")
    csv.to_csv('stock_market.csv', index=False)
    print('Updated')


def download_updates(issuer, last_date, today, driver):
    driver.get('https://www.mse.mk/en/stats/symbolhistory/' + issuer)

    if 'Server Error' in driver.page_source:
        return pd.DataFrame()

    if '503 Service Unavailable' in driver.page_source:
        for i in range(5):
            driver.get('https://www.mse.mk/en/stats/symbolhistory/' + issuer)
            if '503 Service Unavailable' not in driver.page_source:
                break

    to_date = today.replace('-', '/')
    from_date = last_date

    # print(from_date, to_date)

    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#FromDate')))
    from_date_input = driver.find_element(By.CSS_SELECTOR, '#FromDate')
    from_date_input.clear()
    from_date_input.send_keys(from_date)

    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ToDate')))
    to_date_input = driver.find_element(By.CSS_SELECTOR, '#ToDate')
    to_date_input.clear()
    to_date_input.send_keys(to_date)

    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.btn')))
    button_find = driver.find_element(By.CSS_SELECTOR, 'input.btn')
    button_find.click()

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#resultsTable')))
    except TimeoutException:
        return pd.DataFrame()

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.select_one('#resultsTable')

    if table is None:
        return pd.DataFrame()

    rows = []
    tbody = table.find('tbody')
    for tr in tbody.find_all('tr'):
        row = []
        for td in tr.find_all('td'):
            row.append(td.get_text(strip=True))
        rows.append(row)

    headers = ['Date', 'Last trade price', 'Max', 'Min', 'Avg. Price', '%chg.', 'Volume', 'Turnover in BEST in denars',
               'Total turnover in denars']
    df = pd.DataFrame(rows, columns=headers)
    df = df[df['Volume'] != '0']
    df['Issuer'] = issuer

    return df
