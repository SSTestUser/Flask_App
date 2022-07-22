from flask import Flask, render_template, make_response, send_file, jsonify
import textdistance as td
from nltk.stem.porter import PorterStemmer
import os 
import pandas as pd
import re
import string
import json
from collections import Counter
from firebase import Firebase
from firebase_admin import credentials, firestore, initialize_app
import io

# Tokenize document
stemmer = PorterStemmer()


# Limit number of each token occurances to a limit
def limit_tokens(tokens):
    count_tokens = Counter(tokens)
    token_limit = []
    n = 3
    for key,value in count_tokens.items():
        #print([key],value)
        if value > n:
            token_limit.extend([key]*n)
        else:
            token_limit.extend([key]*value)
    return token_limit 

def tokenize(contents):
    contents = contents.lower()
    contents = re.sub(r'[A-Za-z0-9]*@[A-Za-z]*\.?[A-Za-z0-9]*', "", contents)
    contents = re.sub(r'http\S+', '', contents)
    contents = re.sub('[%s]' % re.escape(string.punctuation), '', contents)
    token_clean = []
    for i in contents.split():
        if i in stopwords: 
            #print(i)
            pass
        else:
            #print(i)
            #token_clean.append(i)
            token_clean.append(stemmer.stem(i))
    return limit_tokens(token_clean)   
#    return token_clean   

config = {
    "apiKey": "AIzaSyA4cu_SfbnnuuxQcgM3qVd_YRsvzboUj8Y",
    "authDomain": "surestart-test-app.firebaseapp.com",
    'projectId': "surestart-test-app",
    #"storageBucket": "surestart-test-app.appspot.com",
    "storageBucket":"surestart-test-app.appspot.com",
    "messagingSenderId": "254957547700",
    "appId": "1:254957547700:web:d9736468b87c77ca01a7e1",
    "measurementId": "G-78GX457VSV",
    "databaseURL": "https://surestart-test-app-default-rtdb.firebaseio.com/",
    "serviceAccount" : "./surestart-key.json",
}


app = Flask(__name__)


#firebase = pyrebase.initialize_app(config)
firebase = Firebase(config)
firebase_storage = firebase.storage()

@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"
@app.route('/api/get_resume/<text_resume_name>', methods=['GET'])
def get_resume_pdf(text_resume_name):
    return send_file(firebase_storage.bucket.blob("data_analytics_resumes/"+text_resume_name).download_as_string())
@app.route('/api/get_resume_text/<text_resume_name>', methods=['GET'])
def get_resume(text_resume_name):
    return firebase_storage.bucket.blob("data_analytics_text_resumes/"+text_resume_name).download_as_string().decode('unicode_escape')
@app.route('/api/get_job_description/<job_name>', methods=['GET'])
def get_job_description(job_name):
    return firebase_storage.bucket.blob("job_description/"+job_name).download_as_string().decode('unicode_escape')
@app.route('/api/get_candidates/<candidate_name>', methods=['GET'])
def get_candidates(candidate_name):
    return io.BytesIO(firebase_storage.bucket.blob(candidate_name).download_as_string())
@app.route('/api/get_candidates_ranked/', methods=['GET'])
def get_candidates_ranked():
    return jsonify(json.loads(firebase_storage.bucket.blob('candidates.json').download_as_string().decode('utf-8')))
candidates = pd.read_excel(get_candidates('candidates.xlsx'))
candidates = candidates[["First Name","Last Name","Email","What is your major?","LinkedIn","Citizen/Employment Status","College/University","pdf_loc","text_loc"]]

@app.route('/api/all', methods=['GET'])
def textdistance():
    rankings = {}
    job_des = get_job_description("Job_Description_Data_Analytics.txt")
    for i, row in candidates.iterrows():
        try:
            document = tokenize(get_resume(row['text_loc'])) 
            print(i)
            j = td.jaccard.similarity(document, job_des)
            s = td.sorensen_dice.similarity(document, job_des)
            c = td.cosine.similarity(document, job_des)
            o = td.overlap.normalized_similarity(document, job_des)
            total = (j+s+c+o)/4
            rankings[i] = total
            #print(c)
            #print(rankings)
        except Exception as e:
            print(i,e)
            #input()
            pass

    # print(rankings)
    ranked = sorted(rankings.items(), key=lambda item: item[1])
    # print(ranked)
    candidates_ranked = {}
    for i,j in ranked:
        # print(i)
        #candidates_ranked[candidates['First Name'][i]+" "+candidates['Last Name'][i]] = [candidates['What is your major?'][i],candidates['College/University'][i],candidates['Citizen/Employment Status'][i],i]
        candidates_ranked[i] = candidates.iloc[[i]].to_dict(orient='records')
    # total = (s+o)/2
    
    with open('candidates.json', 'w') as json_file:
        json.dump(candidates_ranked, json_file)    
    return jsonify(candidates_ranked)    

@app.route('/api/get_resumes', methods=['GET'])
def get_resumes():
    file_names = firebase_storage.child("data_analytics_text_resumes/").list_files()
    file_names = [f for f in file_names if "data_analytics_text_resumes/" in f.name]
    
    resume_text = {}

    for file_name in file_names:
        print(file_name.name)
        resume_text[file_name.name] = (file_name.download_as_string()).decode('unicode_escape')
    return json.dumps(resume_text, indent = 4)


if __name__ == '__main__':

    # Initialize Firestore DB
    cred = credentials.Certificate('./surestart-key.json')
    default_app = initialize_app(cred)
    db = firestore.client()
    todo_ref = db.collection('todos')
    
    stopwords =  firebase_storage.bucket.blob("stopwords.txt").download_as_string().decode('unicode_escape').split()
    
    port = int(os.environ.get('PORT', 8080))
    app.config["DEBUG"] = True
    app.run(threaded=True, host='0.0.0.0', port=port)