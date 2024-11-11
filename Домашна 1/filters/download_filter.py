import requests
import pandas as pd
from bs4 import BeautifulSoup

def download_issuers():
    url = 'https://www.mse.mk/en/stats/symbolhistory/adin'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    listIssuers = soup.select('#Code option')
    listIssuers = [issuer for issuer in listIssuers if not any(char.isdigit() for char in str(issuer))]
    listIssuers = [issuer.text.strip() for issuer in listIssuers]
    return listIssuers

