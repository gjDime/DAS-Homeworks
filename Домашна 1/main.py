import pandas as pd
import time
from filters.download_filter import download_issuers
from filters.last_date_filter import last_date
from filters.update_filter import update

start_time = time.time()

update(last_date(download_issuers()))

end_time = time.time()
elapsed_time = end_time - start_time

# Convert to minutes and seconds
minutes, seconds = divmod(elapsed_time, 60)
print(f"Program executed in {int(minutes)} minutes and {seconds:.2f} seconds")