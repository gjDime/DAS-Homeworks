import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


def download_10years(issuer, driver):
    date = datetime.today()
    #    print(issuer)

    # Firefox or Chrome
    driver.get('https://www.mse.mk/en/stats/symbolhistory/' + issuer)
    df_10years = pd.DataFrame()

    for i in range(10):
        to_date = date.strftime('%m/%d/%Y')
        from_date = (date - timedelta(days=365)).strftime('%m/%d/%Y')

        #        print(f"{i + 1} {from_date} {to_date}")
        df_year = download_data(from_date, to_date, issuer, driver)
        df_10years = pd.concat([df_10years, df_year], ignore_index=True)
        date = date - timedelta(days=365)

    return df_10years


def download_data(from_date, to_date, issuer, driver):
    if 'No data' in driver.page_source:
        # print('No data '+from_date+' '+ issuer)
        return pd.DataFrame()

    # WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#FromDate')))
    from_date_input = driver.find_element(By.CSS_SELECTOR, '#FromDate')
    from_date_input.clear()
    from_date_input.send_keys(from_date)

    #     WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ToDate')))
    to_date_input = driver.find_element(By.CSS_SELECTOR, '#ToDate')
    to_date_input.clear()
    to_date_input.send_keys(to_date)

    # WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.btn')))
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
    df['Issuer'] = issuer
    return df


def last_date(listIssuers):
    try:
        dataframe = pd.read_csv('stock_market.csv')
    except:
        dataframe = pd.DataFrame()

    last_date_dict = {}
    # df_all_issuers = pd.DataFrame()

    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    for issuer in listIssuers:
        try:
            issuer_df = dataframe[dataframe['Issuer'] == issuer]
            issuer_df = issuer_df.sort_values(by='Date', ascending=False)
        except KeyError:
            issuer_df = pd.DataFrame()

        if issuer_df.empty:
            issuer_df = download_10years(issuer, driver)
            issuer_df.to_csv('stock_market.csv', mode='a', header=False, index=False)  # 10god worth issuer df

        # df_all_issuers = pd.concat([df_all_issuers, issuer_df], ignore_index=True)

        last_date_issuer = issuer_df['Date'].iloc[0]
        last_date_dict[issuer] = last_date_issuer
    driver.quit()
    # df_all_issuers.to_csv('stock_market.csv', index=False)
    return last_date_dict
