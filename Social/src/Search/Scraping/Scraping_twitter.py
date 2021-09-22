import tweepy as tw
import pandas as pd
from pymongo import MongoClient

def authentication():
    consumer_key = "API Twitter"
    consumer_secret = "API Twitter""
    access_token = "API Twitter""
    access_token_secret = "API Twitter""
    # Creating the authentication object
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    # Setting your access token and secret
    auth.set_access_token(access_token,access_token_secret)
    # Creating the API object while passing in auth information
    api = tw.API(auth)
    return api


def Scraping(search_word, user_id, post_id, dateafter, datebefore, lg='en'):
    search_word = '#'+str(search_word)
    api=authentication()
    # "2021-01-10"
    # "2021-02-10"
    tweets = tw.Cursor(api.search,q=search_word,lang=lg,count=100,result_type="mixed",since=dateafter, until=datebefore).items(1000)
    list_twitte = []
    for tweet in tweets:
        data={
            'User_Screen':tweet.user.screen_name,
            'Created':tweet.created_at,
            'User_location':tweet.user.location,# -- location
            'User_folowers':tweet.user.followers_count,
            'Text':tweet.text
            #'User_id':tweet.user.id,
        }
        list_twitte.append(data)
        data={}
    # save data in mogoDB
    client = MongoClient('localhost', 27017) # connect to mongoDB
    db = client['scraping_db']
    collection_user = db[str(user_id)] # user_id for collection name

    mongo_data = {'project_id': post_id,
                  'src':'twitter',
                  'clean':'no',
                  'data': list_twitte}

    collection_user.insert_one(mongo_data)
    client.close()
