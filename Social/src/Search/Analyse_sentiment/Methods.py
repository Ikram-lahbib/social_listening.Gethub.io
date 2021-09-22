from pymongo import MongoClient
import pandas as pd
import numpy as np
import datetime as dt
import re
import string
from nltk.corpus import stopwords
from googletrans import Translator
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# Model Libraries
from sklearn.metrics import accuracy_score
from sklearn import naive_bayes
from sklearn.linear_model import LogisticRegression
from sklearn import svm
import joblib
import datetime

# -------------- les Methods ------------------

# telechargement de tata
def load_dataset(filename):
    df = pd.read_csv(filename)
    return df
# ajout un label de sentiment a noter data donne une score au text si il positife ou negative ou neuter
def sentiment(df):
    vader = SentimentIntensityAnalyzer()
    df['Scores'] = df['Text'].apply(lambda Text: vader.polarity_scores(Text))
    df['Compound']=df['Scores'].apply(lambda score_dict : score_dict['compound'])
    for i in range(len(df)):
        if df.loc[i,'Compound'] > 0:
            df.loc[i,'Sentiment']=1
        elif df.loc[i,'Compound'] < 0:
            df.loc[i,'Sentiment']=-1
        else:
            df.loc[i,'Sentiment']=0

    return df
# supprimer les colonne unitile
def remove_unwanted_cols(df, cols):
    for col in cols:
        del df[col]
    return df
# netoyage de text les annomalie les ponctuation ...
def nlp_pipeline(text):

    text = text.lower()
    text = text.replace('\n', '').replace('\r', '')
    text = text.replace('rt', '')
    text = ' '.join(text.split())
    text = re.sub(r"[A-Za-z\.]*[0-9]+[A-Za-z%°\.]*", "", text)
    text = re.sub(r"(\s\-\s|-$)", "", text)
    text = re.sub(r"[,\.\!\?\%\(\)\/\"]", "", text)
    text = re.sub(r"\&\S*\s", "", text)
    text = re.sub(r"\&", "", text)
    text = re.sub(r"\+", "", text)
    text = re.sub("(#[A-Za-z0-9_]+)","",text)
    test = re.sub("(http[A-Za-z0-9_]+)","",text)
    text = re.sub(r"\#", "", text)
    text = re.sub("(@[A-Za-z0-9_]+)","",text)
    text = re.sub(r"\$", "", text)
    text = re.sub(r"\£", "", text)
    text = re.sub(r"\%", "", text)
    text = re.sub(r"\:", "", text)
    text = re.sub(r"\…", "", text)
    text = re.sub(r"\@", "", text)
    text = re.sub(r"\-", "", text)
    text = re.sub(r"\“", "", text)
    text = re.sub(r"\”", "", text)
    text = re.sub(r"\'", "", text)
    return text
# supression des emojie
def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)
# traduction
def translet(text):
    translator = Translator()
    translation_text = translator.translate(str(text), dest='en').text
    return translation_text
# tokinisation
def tokenise(translation_text):
    token = word_tokenize(translation_text)
    return token
# lemmitization
def normalise(token):
    lemmatizer = WordNetLemmatizer()
    lemmatized_sentence = []
    for word, tag in pos_tag(token):
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatized_sentence.append(lemmatizer.lemmatize(word, pos))
    return lemmatized_sentence
# supression des stop word
def clean(lemmatized_sentence,stop_words):
    clean =[]
    for token in lemmatized_sentence:
        if token not in stopwords:
            clean.append(token)
    return clean
# cean all data

def cleanall(df):
    for i in range(len(df)):
        try:
            df.loc[i,'Text']= ' '.join(clean(normalise(tokenise(remove_emoji(nlp_pipeline(str(df.loc[i,'Text']))))),stopwords))
        except:
            pass
    return df
# process data
def preprocessData(df):
    ## clolone created
    df['Created'] = pd.to_datetime(df['Created'])
    df['month']   = df['Created'].dt.month
    df['day']   = df['Created'].dt.day
    df['year']  = df['Created'].dt.year
    df['hour']   = df['Created'].dt.hour
    df['minute'] = df['Created'].dt.minute
    df['second'] = df['Created'].dt.second
    ## valeur manqaunt
    return df
# transformez  text a un vecteur
def get_feature_vector(train_fit):
    vector = TfidfVectorizer(sublinear_tf=True)
    vector.fit(train_fit)
    return vector
# prediction de sentiment si score =1 alor positifs
def predSentiment(sentiment):
    if sentiment < 0:
        return "Negatife"
    elif sentiment > 0:
        return "Positife"
    else:
        return "Neutre"

# ============================================================================

def mongo_get_data(collname, post_id, src='twitter'): # befor cleaning

    df = pd.DataFrame() # empty
    client = MongoClient('localhost', 27017)
    # Creation Basede données 'dataTwitter'
    db = client['scraping_db']
    # Creation Collection 'twitters'
    collection = db[str(collname)]

    documents = list(collection.find())
    client.close()
    data = []
    for doc in documents:
        if doc['project_id'] == post_id and doc['src'] == str(src) and doc['clean'] == 'no':
            for dic in doc['data']:
                df=df.append(dic, ignore_index = True)

            return df

def mongo_get_data_youtube(collname, post_id, src='youtube'): # befor cleaning for youtube to clean

    def get_date_clean(a):
        now = datetime.datetime.now()
        l = a.split()
        for word in l:
            if word.isnumeric():
                d = int(word)
            if word.startswith('an'):
                return now - datetime.timedelta(weeks=d*4*12)
            if word.startswith('mois'):
                return now - datetime.timedelta(weeks=d*4)
            if word.startswith('semaine'):
                return now - datetime.timedelta(weeks=d)
            if word.startswith('jour'):
                return now - datetime.timedelta(days=d)
            if word.startswith('heure'):
                return now - datetime.timedelta(hours=d)
            if word.startswith('minute'):
                return now - datetime.timedelta(minutes=d)
        return now - datetime.timedelta(weeks=12)

    df = pd.DataFrame() # empty
    client = MongoClient('localhost', 27017)
    # Creation Basede données 'dataTwitter'
    db = client['scraping_db']
    # Creation Collection 'twitters'
    collection = db[str(collname)]

    documents = list(collection.find())
    client.close()
    date_now = datetime.datetime.now()
    data = []
    for doc in documents:
        if doc['project_id'] == post_id and doc['src'] == str(src) and doc['clean'] == 'no':
            for dic in doc['data']:

                dic['Created'] = get_date_clean(dic['Created'])
                df=df.append(dic, ignore_index = True)

            return df


def mongo_insert_data_after_clean(collname, post_id, df, src='twitter'):

    client = MongoClient('localhost', 27017)
    # Creation Basede données 'dataTwitter'
    db = client['scraping_db']
    # Creation Collection after clean'twitters'
    collection = db[str(collname)]

    list_twitte = []
    for i in range(len(df)):
        data={
             'Text':df.loc[i,'Text'],
             'Score':int(df.loc[i,'Score']),
             'Sentiment':df.loc[i,'Predictions'],
             'User_Screen':df.loc[i,'User_Screen'],
             'User_location':df.loc[i,'User_location'], # -- location
             'User_folowers':df.loc[i,'User_folowers'],
             'year':int(df.loc[i,'year']),
             'month':int(df.loc[i,'month']),
             'day':int(df.loc[i,'day']),
             'hour':int(df.loc[i,'hour']),
             'minute':int(df.loc[i,'minute']),
             'second':int(df.loc[i,'second'])
            }
        list_twitte.append(data)
        data={}
    mongo_data = {'project_id': post_id,
                  'src':str(src),
                  'clean':'yes',
                  'data': list_twitte}
    collection.insert_one(mongo_data)
    client.close()

# ===========================================================================

def SentimentAnalyses(df,modelname,tf_vector, dbname, post_id, src):
    # remove colone unitul
    #df = remove_unwanted_cols(df, ["Unnamed: 0"])
    # cean text
    df = cleanall(df)
    # preprocess data
    df = preprocessData(df)
    # transform text en vecteur
    #tf_vector = CountVectorizer()
    X = tf_vector.transform(np.array(df.loc[:,'Text']).ravel())
    # load Model
    model = joblib.load(modelname)
    # Using Logistic Regression model for prediction
    text_prediction_lr = model.predict(X)
    # Averaging out the hashtags result
    result = pd.DataFrame({'Text': df.Text, 'Score':text_prediction_lr,'User_Screen':df.User_Screen,'User_location':df.User_location,'User_folowers':df.User_folowers,'year':df.year,'month':df.month,'day':df.day,'hour':df.hour,'minute':df.minute,'second':df.second})
    result['Predictions'] =result['Score'].apply(lambda Score: predSentiment(Score))
    mongo_insert_data_after_clean(dbname, post_id, result, src)
