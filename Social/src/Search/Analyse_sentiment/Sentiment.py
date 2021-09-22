from .Methods import *

#import nltk
#nltk.download('averaged_perceptron_tagger')
#nltk.download('wordnet')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import naive_bayes
from sklearn.linear_model import LogisticRegression
from sklearn import svm
import joblib
# =========================================================================


# --------------------- function principal  -------------------------

def train(dbname, post_id, src):

    #def train(namefile, dbname, post_id):
    #df = load_dataset(namefile)
    if src == 'youtube':
        new_df = mongo_get_data_youtube(dbname, post_id, src) # derect from mongoDb no clean df = DataFrame(data)
        df = new_df.copy()
    else:
        new_df = mongo_get_data(dbname, post_id, src) # derect from mongoDb no clean df = DataFrame(data)
        df = new_df.copy()

    #df = new_df.copy()
    # add sentiment
    df = sentiment(df)
    # remove columns
    df = remove_unwanted_cols(df, ['Scores','Compound'])
   # clean data
    df = cleanall(df)
    # vectorize Text
    tf_vector = get_feature_vector(np.array(df.loc[:,'Text']).ravel())
    X = tf_vector.transform(np.array(df.loc[:,'Text']).ravel())
    y = np.array(df.loc[:,'Sentiment']).ravel()
    # split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=30)
    # Training Naive Bayes model
    clf_nb = naive_bayes.MultinomialNB()
    clf_nb.fit(X_train, y_train)
    y_predict_nb = clf_nb.predict(X_test)
    acc_clf_nb=accuracy_score(y_test, y_predict_nb)
    #print(accuracy_score(y_test, y_predict_nb))
    # Training Logistics Regression model
    lr = LogisticRegression(solver='lbfgs')
    lr.fit(X_train, y_train)
    y_predict_lr = lr.predict(X_test)
    acc_lr=accuracy_score(y_test, y_predict_lr)
    #print(accuracy_score(y_test, y_predict_lr))
    # Training SVM Model
    clf_svm_l = svm.SVC(kernel = 'linear' , C=5)
    clf_svm_l.fit(X_train,y_train)
    y_predict_svm = clf_svm_l.predict(X_test)
    acc_svm_l=accuracy_score(y_test,y_predict_svm)
    #print(accuracy_score(y_test,y_predict_svm))
    # Training BernoulliNB
    clf_ber = naive_bayes.BernoulliNB()
    clf_ber.fit(X_train,y_train)
    y_predict_ber = clf_ber.predict(X_test)
    acc_clf_ber=accuracy_score(y_test,y_predict_ber)
    #print(accuracy_score(y_test,y_predict_ber))
    # Save the models
    joblib.dump(clf_nb, 'multinomialNB.sav')
    joblib.dump(lr, 'logistics_Reg.sav')
    joblib.dump(clf_svm_l, 'svm_classifier.sav')
    joblib.dump(clf_ber, 'bernoulliNB.sav')

    dict_acc={'multinomialNB.sav':acc_clf_nb,'logistics_Reg.sav': acc_lr,'svm_classifier.sav': acc_svm_l,'bernoulliNB.sav': acc_clf_ber}
    # bon model
    bon_model=max(dict_acc, key=dict_acc.get)
    print(bon_model)

    #SentimentAnalyses(mongo_get_data(dbname, post_id),bon_model,tf_vector, dbname, post_id)
    SentimentAnalyses(new_df,bon_model,tf_vector, dbname, post_id, src)

# ============================================================================
def mongo_get_data_clean(collname, post_id, src='twitter'): # dateafter cleaning

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
        if doc['project_id'] == post_id and doc['src'] == str(src) and doc['clean'] == 'yes':
            for dic in doc['data']:
                df=df.append(dic, ignore_index = True)

            return df


# ///////////////////////////////// visualisation /////////////////////////////////

def circle(df, user, post_id):
    plt.figure()
    #img1 = plt.subplot(df.Sentiment.value_counts().plot(kind='pie', autopct='%1.0f%%')).figure.savefig("static\\analyse\\img\\"+str(user)+"_"+str(post_id)+"_circle.png")
    img1 = plt.subplot(df.Sentiment.value_counts().plot(kind='pie', autopct='%1.0f%%',title='Le Percentage des Sentiments', figsize=(10,6)))
    plt.savefig("static\\analyse\\img\\"+str(user)+"_"+str(post_id)+"_circle.png")


def Non(df, user, post_id):
    counts = df["Sentiment"].value_counts()
    plt.figure()
    plt.bar(range(len(counts)), counts)
    plt.savefig("static\\analyse\\img\\"+str(user)+"_"+str(post_id)+"_plot.png")

def plot1(df, user, post_id):
    plt.figure()
    sentiment_day = df.groupby(['day', 'Sentiment']).Sentiment.count().unstack()
    sentiment_day.plot(kind='bar',title='Le Nombre des Sentiments Par Jour', figsize=(10,6))
    plt.savefig("static\\analyse\\img\\"+str(user)+"_"+str(post_id)+"_plot1.png")

def plot2(df, user, post_id):
    plt.figure()
    sentiment_hour = df.groupby(['hour', 'Sentiment']).Sentiment.count().unstack()
    sentiment_hour.plot(kind='line',title='Les Sentiment Par Heur', figsize=(10,6))
    plt.savefig("static\\analyse\\img\\"+str(user)+"_"+str(post_id)+"_plot2.png")

def plot3(df, user, post_id):
    plt.figure()
    df2 = df[df['User_location'].map(df['User_location'].value_counts()) >=50]
    airline_sentiment = df2.groupby(['User_location', 'Sentiment']).Sentiment.count().unstack()
    airline_sentiment.plot(kind='bar',title='Les Sentiment Par User Location', figsize=(10,6))
    plt.savefig("static\\analyse\\img\\"+str(user)+"_"+str(post_id)+"_plot3.png")
