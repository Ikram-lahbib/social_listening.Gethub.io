import json
from pymongo import MongoClient

from soupsieve.util import lower
import datetime

def list_dic_comments(chine_comments):

    list_dic = []
    l = chine_comments.split('\n')
    text = ""
    for line in l:
        if line.startswith("Afficher "):
            pass
        else:
            text = text + '\n' + line
    list_info = text.split('RÉPONDRE')
    for info in list_info:
        data = []
        token = info.split('\n')
        for word in token:
            if word != '':
                data.append(word)
        try:
            if not data[-1].isnumeric():
                dat[-1] = 1
            list_dic.append({
                "User_Screen": data[0],
                "Created": data[1],#get_date_clean(data[1]),
                'User_location':"London",
                "User_folowers": int(data[-1]), # likes
                "Text": data[2]

            })
        except:
            pass
    return list_dic


def clean_json_file(filename="static\\data\\data_instance.json"):
    with open(filename, 'w') as json_file:
        print("data it's cleaned")

def save_data_anstence_django_json(list_dic_data, filename="static\\data\\data_instance.json"):
    with open(filename, 'ab') as outfile:
        outfile.seek(0, 2)  # Go to the end of file
        if outfile.tell() == 0:  # Check if file is empty
            outfile.write(json.dumps(list_dic_data).encode())
        else:
            outfile.seek(-1, 2)
            outfile.truncate()  # Remove the last character, open the array
            for dic_data in list_dic_data:
                outfile.write(' , '.encode())  # Write the separator
                outfile.write(json.dumps(dic_data).encode())  # Dump the dictionary
            outfile.write(']'.encode())

# for mongoDB in local
def save_data_in_mongoDB(user_id, post_id, filename="static\\data\\data_instance.json"):
    # open the json_file instane to save in mongoDB
    with open(filename, encoding='utf-8') as json_file:
        try:
            data = json.load(json_file)
        except:
            data = []

    client = MongoClient('localhost', 27017) # connect to mongoDB
    db = client['scraping_db']
    collection_user = db[str(user_id)] # user_id for collection name

    mongo_data = {'project_id': post_id,
                  'src':'youtube',
                  'clean':'no',
                  'data': data}

    collection_user.insert_one(mongo_data)
    client.close()

def delete_data_in_mongoDB(user_id, post_id):

    client = MongoClient('localhost', 27017) # connect to mongoDB
    db = client['countries_db']
    collection_user = db[str(user_id)] # user_id for collection name

    mongo_data = {'project_id': post_id}

    collection_user.delete_one(mongo_data)
    client.close()


# -----------------------------------------------------------------------------------------------------------------------


#test_django()
