from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import glob
import os
import os.path
import pickle

#Iterate through list of S&P 500 to pull docs by ticker
df = pd.read_csv('data/sp500_list.csv')
drop_column = df.columns[0]
df.drop(columns = drop_column, inplace = True)

#Create new dataframe that will be filled with text document index for later
df_doc_index = pd.DataFrame()
df_doc_index['TICKER'] = ''
df_doc_index['FILING_TYPE'] = ''
df_doc_index['FILING_DATE'] = ''
df_doc_index['MD&A_PATH']= ''
df_doc_index['MD&A_TEXT']= ''

mypath = (os.getcwd())
dl = Downloader(mypath+'/dl/')

for i in df.index:
    print(f"{df.index[i]}: Downloading Ks & Qs for {df.COMPANY[i]}")
    dl.get("10-K", df.TICKER[i], after_date="20190101", include_amends=False)
    dl.get("10-Q", df.TICKER[i], after_date="20190101", include_amends=False)
    print(f"{df.index[i]}: {df.COMPANY[i]} filing download done.")
    file_list_Q = glob.glob(mypath+f'/dl/sec_edgar_filings/{df.TICKER[i]}/10-Q/*.txt')
    file_list_K = glob.glob(mypath+f'/dl/sec_edgar_filings/{df.TICKER[i]}/10-K/*.txt')
    
    print(f"{df.index[i]}: Extracting text from {df.COMPANY[i]} 10Qs.")
    
    for file_name in file_list_Q:
        with open(file_name) as html_file:
            soup = BeautifulSoup(open(file_name), 'lxml')
            text = soup.get_text('\n\n')
            text_lines = text.splitlines()
            filing_string = ''
            date_string = ''
            keep_lines = []
            
            for text_line in text_lines:
                if 'FILED AS OF DATE' in text_line:
                    date_string = text_line.strip()[-8:]
                    break
            #This doesn't work for 50% of the filings       
            for idx, text_line in enumerate(text_lines):
                if 'ITEM' in text_line and '2' in text_line:
                    keep_lines.append(idx)
                if 'ITEM' in text_line and '3' in text_line:
                    keep_lines.append(idx)
                    
            filing_string = text_lines[keep_lines[0]:keep_lines[1]]
            filing_string = ' '.join(filing_string)
            
            path = mypath+f'/dl/sec_edgar_filings/{df.TICKER[i]}/10-Q/'
            filename = f'{df.TICKER[i]}-10Q-MD&A-{date_string}.txt'
            
            with open(os.path.join(path, filename), 'w+', encoding='utf-8') as f:
                f.write(filing_string)
                
            index_row = {'TICKER':df.TICKER[i], 'FILING_TYPE':'10Q', 'FILING_DATE':date_string,
                         'MD&A_PATH':path+filename, 'MD&A_TEXT':filing_string}
            df_doc_index = df_doc_index.append(index_row, ignore_index=True)
    
    print(f"{df.index[i]}: Extracting text from {df.COMPANY[i]} 10Ks.")
    
    for file_name in file_list_K:
        with open(file_name) as html_file:
            soup = BeautifulSoup(open(file_name), 'lxml')
            text = soup.get_text('\n\n')
            text_lines = text.splitlines()
            filing_string = ''
            date_string = ''
            keep_lines = []
            
            for text_line in text_lines:
                if 'FILED AS OF DATE' in text_line:
                    date_string = text_line.strip()[-8:]
                    break
                    
            for idx, text_line in enumerate(text_lines):
                if 'ITEM' in text_line and '2' in text_line:
                    keep_lines.append(idx)
                if 'ITEM' in text_line and '3' in text_line:
                    keep_lines.append(idx)
                    
            filing_string = text_lines[keep_lines[0]:keep_lines[1]]
            filing_string = ' '.join(filing_string)
            
            path = mypath+f'/dl/sec_edgar_filings/{df.TICKER[i]}/10-K/'
            filename = f'{df.TICKER[i]}-10K-MD&A-{date_string}.txt'
            
            with open(os.path.join(path, filename), 'w+', encoding='utf-8') as f:
                f.write(filing_string)
                
            index_row = {'TICKER':df.TICKER[i], 'FILING_TYPE':'10K', 'FILING_DATE':date_string,
                         'MD&A_PATH':path+filename, 'MD&A_TEXT':filing_string}
            df_doc_index = df_doc_index.append(index_row, ignore_index=True)

df_doc_index.to_pickle('md&a_text_doc_index.pkl')