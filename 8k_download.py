import numpy as np
import pandas as pd
from sec_edgar_downloader import Downloader

df = pd.read_csv('sp500_test.csv')
drop_column = df.columns[0]
df.drop(columns = drop_column, inplace = True)
dl = Downloader('test_data/')
for i in df.index:
    print(f"{df.index[i]}: Pulling 8Ks for {df.COMPANY[i]}")
    dl.get("8-K", df.TICKER[i], after_date="20180101", include_amends=False)
    print(f"{df.index[i]}: {df.COMPANY[i]} done.")
    