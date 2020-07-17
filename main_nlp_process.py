
from sec_nlp_utils import *
TICKER_LIST = 'test_ticker_list.csv'

class NLPText(object):
    def __init__(self,df,ticker): #just a dataframe of sentences with href key
        self.df_tokenized = df
        self.ticker = ticker
        self.NLTK_sentiment()
    
    def BERT(self):
        pass

    def NLTK_sentiment(self): #score each sentence
        sid = SentimentIntensityAnalyzer()
        for i,row in self.df_tokenized.iterrows():
            sentence = row['sentence_text']
            sentence = filter_stopwords(sentence)
            ss = sid.polarity_scores(sentence)
            for ss_key in ss.keys():
                self.df_tokenized.at[i,ss_key] = ss[ss_key]
        return

    def match_keywords(self,keyword_list,keyword_list_name): #return match list of keyword, sentence id, one to many
        for i,row in self.df_tokenized.iterrows():
            sentence = row['sentence_text']
            sentence = filter_stopwords(sentence)
            list_found = check_if_list_found_in_text(sentence,keyword_list)
            if len(list_found) >= 1:
                num_found = len(list_found)
                try:
                    self.df_tokenized.at[i,keyword_list_name] = str(list_found)
                    self.df_tokenized.at[i,keyword_list_name+'_number'] = num_found
                except:
                    print("Error: "+str(list_found)+":"+str(i))
        return

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
                if 'mdna' not in f and 'index' not in f: #make this better
                    df = pd.read_csv(file_path + f)
                    df['file']=f
                    df['href']=href
                    list_text.append(df)
        self.df_text = pd.concat(list_text)
        self.df_text['lowercase'] = self.df_text['text'].str.lower()
        return 
    
    def get_business_segments(self):
        i = np.flatnonzero(self.df_text['lowercase'].str.contains('business segment results'))
        if len(i) == 0:
            i = np.flatnonzero(self.df_text['lowercase'].str.contains('business segment'))
        if len(i) == 0:
            return

        list_phrases = []
        for item in i[:2]:
            text = ' '.join(list(self.df_text[item:item+10]['text']))
            blob = TextBlob(text)
            blob.tags           
            list_phrases.append(list(blob.noun_phrases))
        list_nouns = two_list_union(list_phrases[0],list_phrases[1])

        list_nouns = [x for x in list_nouns if not any(c.isdigit() for c in x)]
        list_nouns = [re.sub(r"[-()\"\$\%#/@;:<>{}`+=~|.!?,]", "", x) for x in list_nouns]
        list_nouns = [x.strip(' ') for x in list_nouns]
        list_filter = list(pd.read_csv(FNCL_TERMS_CSV,header=None)[0])
        list_main = np.setdiff1d(list_nouns,list_filter)
        list_filter = list(pd.read_csv(CORP_TERMS_CSV,header=None)[0])
        list_main = np.setdiff1d(list_main,list_filter)
        list_filter = list(pd.read_csv(LEGAL_TERMS_CSV,header=None)[0])
        list_main = np.setdiff1d(list_main,list_filter)
        self.list_segments = list(list_main)
        while("" in self.list_segments) : 
            self.list_segments.remove("")
        return

class SECTextData(object):
    def __init__(self, ticker):
        self.ticker = ticker
        self.get_files_list()
        self.get_full_text()
        self.get_mdna_text()
        self.get_business_segments()

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
        if len(list_mdna) > 0:
            self.df_mdna = pd.concat(list_mdna)
        return

def score_files(csv, force = False):
    df_ticker_list = pd.read_csv(csv)

    df_file_list = pd.read_csv(FILE_INDEX)

    for i, row in df_ticker_list.iterrows():

        ticker = row['Symbol']
        ticker = 'AXP'
        ticker = ticker.upper()
        file_path = SCORED_DATA_PATH + ticker
        file_name = file_path+"/"+ticker+'_keywords.csv'

        if force == False:
            if os.path.exists(file_name):
                print("File exists: "+file_name)
                continue

        df_filter = df_file_list.loc[df_file_list['ticker']==ticker]
        archive_dir = list(df_filter['href'])[0]
        archive_dir = archive_dir.replace("https://www.sec.gov",str(LOCAL_PATH))
        archive_dir_list = archive_dir.split('/')
        archive_path = ''
        for s in archive_dir_list[:-2]:
            if len(s)>0:
                archive_path = archive_path+"/"+s
        archive_path = archive_path + "/"
            
        print('Working for '+ticker+" at "+archive_path)

        if not os.path.exists(archive_path):
            print("Missing directory: "+archive_path)
            continue

        try:
            os.makedirs(file_path, exist_ok=True)
        except OSError:
            print ("Directory %s failed" % file_path)
        else:
            print ("Successfully created the directory %s " % file_path)

        try:
            print("SEC object")
            obj_sec = SECTextData(ticker)
        except:
            print ("failed creating SECTextData for "+ticker)
            continue

        if hasattr(obj_sec,"df_mdna") == False:
            print ("MDNA false: continue")
            continue

        if hasattr(obj_sec,"list_segments") == False:
            print ("List segments false: continue")
            continue

        print("NLP object")
        obj_nlp = NLPText(obj_sec.df_mdna,ticker)
        obj_nlp.match_keywords(obj_sec.list_segments,'segments')

        df = obj_nlp.df_tokenized
        df_out = split_keywords(df)

        print("Munge data")
        df_out = df_out.groupby(['href','keyword']).mean().reset_index()
        df_fi = pd.read_csv('file_index.csv')
        df_fi['filing_date'] = pd.to_datetime(df_fi['filing_date...4'])
        df_fi['period_date'] = pd.to_datetime(df_fi['period_date'])
        df_fi = df_fi[['ticker','href','period_date','filing_date']]
        df_fi = df_fi.groupby('href').first()
        df_merged = pd.merge(df_out,df_fi,how = 'inner',left_on = 'href',right_on = 'href')
        df_merged = df_merged.sort_values('filing_date',ascending = False)
    
        print("Write to file")
        df_merged.to_csv(file_name)
        break

score_files(TICKER_LIST,force = False)

#SECTION or TOPIC modeling
#revenue recognition
#join venture
#related party
#acquisitions
#commissions
#receivables
#dividends
