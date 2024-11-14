import pandas as pd
import time
from filters.download_filter import download_issuers
from filters.last_date_filter import last_date
from filters.update_filter import update

start_time = time.time()
update(last_date(download_issuers()))
# df = pd.read_csv('stock_market.csv', low_memory=False)
# df.sort_values(by='Issuer', ascending=True)
# df.to_csv('stock_market.csv', index=False)
#
# df['Date'] = df['Date'].astype(str)
# df['Issuer'] = df['Issuer'].astype(str)
# for col in df.columns[1:-1]:
#     df[col] = pd.to_numeric(df[col], errors='coerce')

# print(df.dtypes)
# print(df.isnull().sum())
# print(df[df['Volume'].isna()])
# df.to_csv('stock_market.csv', index=False)


end_time = time.time()
elapsed_time = end_time - start_time

# Convert to minutes and seconds
minutes, seconds = divmod(elapsed_time, 60)
print(f"Program executed in {int(minutes)} minutes and {seconds:.2f} seconds")