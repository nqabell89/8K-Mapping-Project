
import os
import pandas as pd
import pathlib
from os import listdir
from os.path import isfile, join

LOCAL_PATH = pathlib.Path().absolute()

class SECTextData(object):
    def __init__(self, ticker):
        self.ticker = ticker

    def get_files_list(self):
        self.df_file_index = (pd.read_csv('file_index.csv'))
        self.df_file_index = self.df_file_index.loc[self.df_file_index['ticker']==self.ticker]
        self.list_href = list(self.df_file_index['href'])

    def get_mdna_text(self):
        list_mdna = []
        for href in self.list_href:
            file_name = href.replace("https://www.sec.gov",str(LOCAL_PATH))
            file_name_list = file_name.split('/')
            file_path = ''
            for s in file_name_list[:-1]:
                if len(s)>0:
                    file_path = file_path+"/"+s
            file_path = file_path + "/"
            only_files = [f for f in listdir(file_path) if isfile(join(file_path, f))]
            for f in only_files:
                if 'mdna' in f:
                    df_mdna = pd.read_csv(file_path + f)
                    df_mdna['file']=f
                    df_mdna['href']=href
                    list_mdna.append(df_mdna)
        return pd.concat(list_mdna)

    def get_full_text(self):
        list_text = []
        for href in self.list_href:
            file_name = href.replace("https://www.sec.gov",str(LOCAL_PATH))
            file_name_list = file_name.split('/')
            file_path = ''
            for s in file_name_list[:-1]:
                if len(s)>0:
                    file_path = file_path+"/"+s
            file_path = file_path + "/"
            only_files = [f for f in listdir(file_path) if isfile(join(file_path, f))]
            for f in only_files:
                if 'mdna' not in f and self.ticker in f:
                    df = pd.read_csv(file_path + f)
                    df['file']=f
                    df['href']=href
                    list_text.append(df)
        return pd.concat(list_text)

sec_obj = SECTextData('AXP')
sec_obj.get_files_list()
sec_obj.get_mdna_text()
print(sec_obj.df_file_index)