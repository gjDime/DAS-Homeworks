import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime

from filters.download_filter import download_issuers
from filters.last_date_filter import tacna_funkcija

# tables = download_filter()
#check_last_date(download_data())
#print(datetime.today().date())
#table.to_csv('test.csv', index=False)
tacna_funkcija(download_issuers())


# df = pd.read_csv('test.csv')
#
# url = 'https://www.mse.mk/mk/stats/symbolhistory/adin'
# response = requests.get(url)
# soup = BeautifulSoup(response.text, 'html.parser')
#
# listIssuers = soup.select('#Code option')
# listIssuers = [issuer for issuer in listIssuers if not any(char.isdigit() for char in str(issuer))]
# print(len(listIssuers))
