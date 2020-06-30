import numpy as np
import pandas as pd
from sec_edgar_downloader import Downloader

df = pd.read_csv('data/sp500_list.csv')
drop_column = df.columns[0]
df.drop(columns = drop_column, inplace = True)
df.CIK = df.CIK.astype(str)
df['CIK'] = df['CIK'].str.zfill(10)
dl = Downloader('data/')
for i in df.index:
    print(f"{df.index[i]}: Pulling 8Ks for {df.COMPANY[i]}")
    dl.get("8-K", df.CIK[i], after_date="20070101", include_amends=False)
    print(f"{df.index[i]}: {df.COMPANY[i]} done.")
    