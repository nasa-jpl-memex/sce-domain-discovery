from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import StratifiedKFold
from sklearn import linear_model
from sklearn.externals import joblib
import flask
import numpy as np
import os
from flask import request, redirect, flash, url_for
from werkzeug.utils import secure_filename

accuracy = 0.0
splits = 2
iteration = 1

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


def update_model(annotations):
    global accuracy, splits, iteration
    clf = None
    keywords = getattr(flask.current_app, 'keywords', None)
    if keywords is None:
        keywords = load_vocab()
        clf = setattr(flask.current_app, 'keywords', keywords)
        clf = linear_model.SGDClassifier()
    if clf is None:
        clf = getattr(flask.current_app, 'clf', None)
    url_text = getattr(flask.current_app, 'url_text', None)
    if url_text is None or clf is None:
        print('An error occurred while accessing the application context variables')
        return '-1'
    count_vect = CountVectorizer(lowercase=True, stop_words='english', vocabulary=keywords.keys())
    features = count_vect.fit_transform(url_text).toarray().astype(np.float64)
    labeled = np.array(annotations)

    print('No. of features: ' + str(len(features)) + ' and No. of labels: ' + str(len(labeled)))

    clf.partial_fit(features, labeled, classes=np.unique(labeled))
    predicted = clf.predict(features)
    accuracy = (labeled == predicted).sum() / float(len(labeled))

    '''
    for i in xrange(0, iteration):
        local_acc = 0.0
        skf = StratifiedKFold(n_splits=splits, shuffle=True)
        skf.get_n_splits(features, labeled)
        for train_index, test_index in skf.split(features, labeled):
            # print("TRAIN:", len(train_index), "TEST:", len(test_index))
            X_train, X_test = features[train_index], features[test_index]
            y_train, y_test = labeled[train_index], labeled[test_index]

            # print("X Train:", X_train, "Y Train:", y_train)
            clf.partial_fit(X_train, y_train, classes=np.unique(labeled))
            predicted = clf.predict(X_test)
            local_acc += (y_test == predicted).sum() / float(len(y_test))
        print("Iter " + str(i + 1) + " and Accuracy: " + str(local_acc / splits))
        accuracy = local_acc / splits
    '''
    setattr(flask.current_app, 'clf', clf)
    return str(accuracy)


def predict(txt):
    keywords = getattr(flask.current_app, 'keywords', None)
    if keywords is None:
        return -1
    clf = getattr(flask.current_app, 'clf', None)
    if clf is None:
        return -1
    count_vect = CountVectorizer(lowercase=True, stop_words='english', vocabulary=keywords.keys())
    features = count_vect.fit_transform([txt]).toarray().astype(np.float64)
    predicted = clf.predict(features)
    print(predicted)
    return predicted[0]

def import_model():
    global accuracy
    keywords = getattr(flask.current_app, 'keywords', None)
    filename = 'model.pkl'

    if keywords is None:
        keywords = load_vocab()
        clf = setattr(flask.current_app, 'keywords', keywords)
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

    # clf = joblib.load(os.path.join(flask.current_app.root_path, flask.current_app.config['UPLOAD_FOLDER'], filename))
    dict = joblib.load(os.path.join(flask.current_app.root_path, flask.current_app.config['UPLOAD_FOLDER'], filename))
    accuracy = dict['Accuracy']
    clf = dict['Model']
    setattr(flask.current_app, 'clf', clf)

    return str(accuracy)


def export_model():
    global accuracy
    clf = getattr(flask.current_app, 'clf', None)
    fname = 'model.pkl'
    # joblib.dump(clf, fname)
    dict = {'Accuracy': accuracy, 'Model': clf}
    joblib.dump(dict, fname)
    return flask.send_from_directory(directory=flask.current_app.root_path + '/../', filename=fname)


def check_model():
    clf = getattr(flask.current_app, 'clf', None)
    if clf is None:
        return str(-1)
    return str(0)
