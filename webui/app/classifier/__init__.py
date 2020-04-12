from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.externals import joblib
import flask
import numpy as np
import os
from flask import request, flash
from sklearn.ensemble import RandomForestClassifier
from pyArango.connection import *
import pickle
from flask import current_app as app
from app.models.model import set_sparkler_defaults

accuracy = 0.0
splits = 2
iteration = 1

db = None
models = None
aurl = os.getenv('ARANGO_URL', 'https://single-server-int:8529')
conn = Connection(aurl, 'root', '', verify=False)
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


def new_model(name):
    model = models.createDocument()
    model['name'] = name
    model._key = name
    model.save()
    set_sparkler_defaults(name)
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
    clf = RandomForestClassifier(n_estimators=100)
    count_vect = CountVectorizer(lowercase=True, stop_words='english')
    tfidftransformer = TfidfTransformer()

    if url_text is None:
        print('An error occurred while accessing the application context variables')
        return '-1'

    labeled = np.array(annotations)

    if model['labeled'] is not None:
        # add the old docs to the new
        prev_url_text = model['url_text']
        prev_labeled = model['labeled']
        prev_url_details = model['url_details']
        url_text = np.append(url_text, prev_url_text, axis=0)
        labeled = np.append(labeled, prev_labeled, axis=0)
        url_details = np.append(url_details, prev_url_details, axis=0)

    features = count_vect.fit_transform(url_text)
    features = tfidftransformer.fit_transform(features).toarray().astype(np.float64)

    print('No. of features: ' + str(len(features)) + ' and No. of labels: ' + str(len(labeled)))

    print(np.unique(labeled))
    clf.fit(features, labeled, )

    # save the model
    model['url_test'] = url_text
    if isinstance(url_details, np.ndarray):
        model['url_details'] = url_details.tolist()
    else:
        model['url_details'] = url_details
    model['labeled'] = labeled.tolist()
    encoded_model = {'countvectorizer': count_vect, 'tfidftransformer': tfidftransformer, 'clf': clf}
    with open('/models/' + model['name'] + '.pickle', 'wb') as handle:
        pickle.dump(encoded_model, handle, protocol=pickle.HIGHEST_PROTOCOL)
    model.save()
    predicted = clf.predict(features)
    accuracy = (labeled == predicted).sum() / float(len(labeled))

    dictionary = get_metrics(model)
    json_dictionary = json.dumps(dictionary)
    return json_dictionary


def get_metrics(model):
    unique, counts = np.unique(model['labeled'], return_counts=True)
    dictionary = dict(zip(unique, counts))

    return dictionary


def predict(m, txt):
    model = models[m]
    encoded_model = {}

    if (os.path.isfile('/models/' + model['name'] + '.pickle')):
        with open('/models/' + model['name'] + '.pickle', 'rb') as handle:
            encoded_model = pickle.load(handle)

    if ('countvectorizer' in encoded_model):
        test = encoded_model['countvectorizer']
    if model is None:
        app.logger.info("Model not found")
        return -1
    elif 'countvectorizer' not in encoded_model or encoded_model['countvectorizer'] is None:
        app.logger.info("No Count Vectorizer")
        return -1

    app.logger.info('Sorting Count Vectorizer out ' + model['name'])
    count_vect = encoded_model['countvectorizer']
    tfidftransformer = encoded_model['tfidftransformer']
    clf = encoded_model['clf']

    features = count_vect.transform([txt])
    features = tfidftransformer.transform(features).toarray().astype(np.float64)

    predicted = clf.predict(features)
    return predicted[0]


def import_model():
    global accuracy
    print('importing')
    filename = 'model.pkl'

    if 'file' not in request.files:
        flash('No file part')
        return '-1'
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return '-1'
    if file:
        file.save(os.path.join(flask.current_app.root_path, flask.current_app.config['UPLOAD_FOLDER'], filename))
    else:
        flash('An error occurred while uploading the file')
        return '-1'

    model = joblib.load(os.path.join(flask.current_app.root_path, flask.current_app.config['UPLOAD_FOLDER'], filename))

    accuracy = model['accuracy']

    setattr(flask.current_app, 'model', model)

    dictionary = get_metrics(model)
    json_dictionary = json.dumps(dictionary)

    return json_dictionary


def export_model(m):
    return flask.send_from_directory(directory='/models/', filename=m + '.pickle')


def check_model(m):
    model = models[m]
    if model is None:
        return str(-1)

    dictionary = get_metrics(model)
    json_dictionary = json.dumps(dictionary)

    return json_dictionary
