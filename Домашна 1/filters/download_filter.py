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

# def download_data():
#     listIssuers = download_issuers()
#
#     all_dfs = []
#     for issuer in listIssuers:
#         all_dfs.append(download_issuer(issuer))
#
#     final_df = pd.concat(all_dfs, ignore_index=True)
#     #cols = ['Issuer'] + [col for col in final_df.columns if col != 'Issuer']
#     # final_df = final_df[cols]
#
#     return all_dfs