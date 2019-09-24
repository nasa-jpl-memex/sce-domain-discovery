from pickle import dumps, loads
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.externals import joblib
import flask
import numpy as np
import os
import json
from flask import request, flash
# from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from pyArango.connection import *
import pickle

accuracy = 0.0
splits = 2
iteration = 1

db = None
models = None
aurl = os.getenv('ARANGO_URL', 'https://single-server-int:8529')
conn = Connection(aurl, 'root', '',verify=False)
if not conn.hasDatabase("sce"):
    db = conn.createDatabase("sce")
else:
    db = conn["sce"]

if not db.hasCollection('models'):
    models = db.createCollection('Collection', name='models')
else:
    models = db.collections['models']


def load_vocab():
    """Load Vocabulary"""
    #with open("/Users/ksingh/git-workspace/dd-polar/seedexplorer/src/main/resources/data/keywords.txt", 'rb') as f:
    if os.path.exists('keywords.txt'):
        with open("keywords.txt", 'rb') as f:
            keywords_content = f.read()
    else:
        with open("keywords.txt", 'wb') as fw:
            fw.write("This is a test")
            keywords_content = "This is a test"
    count_vect = CountVectorizer(lowercase=True, stop_words='english')
    count_vect.fit_transform([keywords_content])
    keywords = count_vect.vocabulary_
    return keywords


# def clear_model():
#     print('clear_model')
#     fname = 'model.pkl'
#     if os.path.isfile(fname):
#         os.remove(fname)
#     setattr(flask.current_app, 'model', None)
#     return '0'

def new_model(name):
    ## Needs to create model in database, with name an initial crawl urls etc

    model = models.createDocument()
    model['name'] = name
    model._key = name
    model.save()
    print('create new model')

def get_models():
    aql = "FOR model IN models RETURN {name: model.name}"
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=1)
    return list(queryResult)

def update_model(m, annotations):
    global accuracy, splits, iteration

    model = models[m]

    if model['url_text'] is not None:
        url_text = model['url_text']
    else:
        url_text = None

    if model['url_details'] is not None:
        url_details = model['url_details']
    else:
        url_details = None
    # clf = MLPClassifier(max_iter=1000, learning_rate='adaptive',)
    clf=RandomForestClassifier(n_estimators=100)
    count_vect = CountVectorizer(lowercase=True, stop_words='english')
    tfidftransformer = TfidfTransformer()

    if url_text is None:
        print('An error occurred while accessing the application context variables')
        return '-1'

    labeled = np.array(annotations)
    #model=getattr(flask.current_app, 'model', None)

    if model['labeled'] is not None:
        # add the old docs to the new
        prev_url_text=model['url_text']
        prev_labeled=model['labeled']
        prev_url_details=model['url_details']
        url_text=np.append(url_text,prev_url_text,axis=0)
        labeled=np.append(labeled,prev_labeled,axis=0)
        url_details=np.append(url_details,prev_url_details,axis=0)

    features = count_vect.fit_transform(url_text)
    features=tfidftransformer.fit_transform(features).toarray().astype(np.float64)

    print('No. of features: ' + str(len(features)) + ' and No. of labels: ' + str(len(labeled)))

    print np.unique(labeled)
    clf.fit(features, labeled,)

    # save the model
    model['url_test'] = url_text
    if isinstance(url_details, np.ndarray):
        model['url_details'] = url_details.tolist()
    else:
        model['url_details'] = url_details
    model['labeled'] = labeled.tolist()
    #cv = dumps(count_vect,0)
    #model['countvectorizer'] = base64.encodestring(dumps(count_vect,0))
    #model['tfidftransformer'] = base64.encodestring(dumps(tfidftransformer,0))
    #model['clf'] = base64.encodestring(dumps(clf,0))
    encoded_model = {'countvectorizer': count_vect, 'tfidtransformer': tfidftransformer, 'clf': clf}
    with open('/models/'+model['name']+'.pickle', 'wb') as handle:
        pickle.dump(encoded_model, handle, protocol=pickle.HIGHEST_PROTOCOL)
    #setattr(flask.current_app, 'model', model)
    model.save()
    predicted = clf.predict(features)
    accuracy = (labeled == predicted).sum() / float(len(labeled))

    #fname = 'model.pkl'
    #joblib.dump(model, fname)

    dictionary = get_metrics(model)
    json_dictionary = json.dumps(dictionary)

    #return str(accuracy)
    return json_dictionary


def get_metrics(model):
    unique, counts = np.unique(model['labeled'], return_counts=True)
    dictionary = dict(zip(unique, counts))

    return dictionary


def predict(m, txt):

    model = models[m]
    encoded_model = None
    if(os.path.isfile('/models/'+model['name']+'.pickle')):
        with open('/models/'+model['name']+'.pickle', 'rb') as handle:
            encoded_model = pickle.load(handle)

    print("Creating Prediction Model, looking for: "+m)
    if model is None:
        print("Model not found")
        return -1
    elif encoded_model['countvectorizer'] is None:
        print("No Count Vectorizer")
        return -1

    count_vect = encoded_model['countvectorizer']
    tfidftransformer = encoded_model['tfidftransformer']
    clf= encoded_model['clf']

    features = count_vect.transform([txt])
    features=tfidftransformer.transform(features).toarray().astype(np.float64)

    predicted = clf.predict(features)
    print("Prediction")
    print(predicted)
    return predicted[0]

def import_model():
    global accuracy
    print 'importing'
    filename = 'model.pkl'


    if 'file' not in request.files:
        flash('No file part')
        return '-1'
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return '-1'
    if file:
        # filename = secure_filename(file.filename)
        file.save(os.path.join(flask.current_app.root_path, flask.current_app.config['UPLOAD_FOLDER'], filename))
        # return redirect(url_for('uploaded_file', filename=filename))
    else:
        flash('An error occurred while uploading the file')
        return '-1'

    model = joblib.load(os.path.join(flask.current_app.root_path, flask.current_app.config['UPLOAD_FOLDER'], filename))

    accuracy = model['accuracy']

    setattr(flask.current_app, 'model', model)

    dictionary = get_metrics(model)
    json_dictionary = json.dumps(dictionary)

    # return str(accuracy)
    return json_dictionary


def export_model(m):
    global accuracy
    #model = getattr(flask.current_app, 'model', None)
    model = models[m]

    if model is None:
        return -1

    model['accuracy']=accuracy

    fname = 'model.pkl'
    joblib.dump(model, fname)

    return flask.send_from_directory(directory=flask.current_app.root_path + '/../', filename=fname)


def check_model(m):
    #model = getattr(flask.current_app, 'model', None)
    model = models[m]
    if model is None:
        return str(-1)

    dictionary = get_metrics(model)
    json_dictionary = json.dumps(dictionary)

    # return str(0)
    return json_dictionary

def save_seeds(m, data):
    model = models[m]
    model['seed_urls'] = data.splitlines()
    model.save()
