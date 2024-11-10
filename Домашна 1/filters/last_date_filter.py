import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from selenium.common.exceptions import TimeoutException


def download_10years(issuer):
    date = datetime.today()
    print(issuer)

    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)  # Firefox or Chrome
    driver.get('https://www.mse.mk/en/stats/symbolhistory/' + issuer)
    df_10years = pd.DataFrame()

    for i in range(10):
        to_date = date.strftime('%m/%d/%Y')
        from_date = (date - timedelta(days=365)).strftime('%m/%d/%Y')

        print(f"{i + 1} {from_date} {to_date}")
        df_year = download_year(from_date, to_date, issuer, driver)
        df_10years = pd.concat([df_10years, df_year], ignore_index=True)
        date = date - timedelta(days=365)
    driver.quit()

# TODO
    # if len(df_10years) == 0:
    #     row = [datetime.today()] + [''] * 8
    #     df_10years = pd.DataFrame([row])

    return df_10years


def download_year(from_date, to_date, issuer, driver):
    # url = 'https://www.mse.mk/en/stats/symbolhistory/' + issuer
    # driver.get('https://www.mse.mk/en/stats/symbolhistory/' + issuer)

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

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#resultsTable')))
    except TimeoutException:
        return pd.DataFrame()
    table = driver.find_element(By.CSS_SELECTOR, '#resultsTable')

    headers = ['Date', 'Last trade price', 'Max', 'Min', 'Avg. Price', '%chg.', 'Volume', 'Turnover in BEST in denars',
               'Total turnover in denars']
    # thead = table.find_element(By.TAG_NAME, 'thead')  # Re-locate the 'thead'
    # for th in thead.find_elements(By.TAG_NAME, 'th'):  # Find all 'th' elements in the 'thead'
    #     headers.append(th.text.strip())

    rows = []
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    for tr in tbody.find_elements(By.TAG_NAME, 'tr'):
        row = []
        for td in tr.find_elements(By.TAG_NAME, 'td'):
            row.append(td.text.strip())
        rows.append(row)

    df = pd.DataFrame(rows, columns=headers)
    df = df.dropna(subset=['Date'])
    df = df[df['Volume'] != '0']
    df['Issuer'] = issuer
    return df


def last_date(listIssuers):
    try:
        dataframe = pd.read_csv('stock_market.csv')
    except:
        dataframe = pd.DataFrame()

    last_date_dict = {}
    df_all_issuers = pd.DataFrame()
    for issuer in listIssuers:
        try:
            issuer_df = dataframe[dataframe['Issuer'] == issuer]
        except KeyError:
            issuer_df = pd.DataFrame()

        if len(issuer_df) == 0:
            issuer_df = download_10years(issuer)
            issuer_df.to_csv('stock_market.csv', mode='a', header=False, index=False)  # 10god worth issuer df

        # df_all_issuers = pd.concat([df_all_issuers, issuer_df], ignore_index=True)
        last_date_issuer = datetime.today().strftime('%m-%d-%Y')
        last_date_dict[issuer] = last_date_issuer

    # df_all_issuers.to_csv('stock_market.csv', index=False)
    return last_date_dict
