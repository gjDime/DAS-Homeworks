import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime

from filters.download_filter import download_issuers
from filters.last_date_filter import last_date
from filters.update_filter import update


update(last_date(download_issuers()))
