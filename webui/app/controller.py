from flask import Blueprint, request, render_template, redirect, url_for, send_from_directory
from app import classifier
from flask_cors import CORS
import requests
import os
# Define Blueprint(s)
mod_app = Blueprint('application', __name__, url_prefix='/explorer')
CORS(mod_app)

# Define Controller(s)
@mod_app.route('/')
def index():
    return send_from_directory('static/pages', 'index.html')

@mod_app.route('/classify/createnew/<model>', methods=['GET'])
def create_new_model(model):
    ## TODO need to deal with naming models
    print("here")
    #classifier.clear_model()
    classifier.new_model(model)
    return("done")



# POST Requests
@mod_app.route('/classify/update/<model>', methods=['POST'])
def build_model(model):
    ## TODO Specify model
    annotations = []
    data = request.get_data()
    for item in data.split('&'):
        annotations.append(int(item.split('=')[1]))
    accuracy = classifier.update_model(model, annotations)
    return accuracy


@mod_app.route('/classify/upload/<model>', methods=['POST'])
def upload_model(model):
    ## TODO Specify model
    return classifier.import_model(model)


@mod_app.route('/classify/download/<model>', methods=['POST'])
def download_model(model):
    ## TODO Specify model
    return classifier.export_model(model)


@mod_app.route('/classify/exist/<model>', methods=['POST'])
def check_model(model):
    ## TODO Specify model
    return classifier.check_model(model)


@mod_app.route('/cmd/crawler/exist/<model>', methods=['POST'])
def check_crawl_exists(model):
    ## TODO Specify model
    ## TODO FIX URL for scale out
    return requests.post("http://sparkler:6000/cmd/crawler/exist/").text


@mod_app.route('/cmd/crawler/crawl/<model>', methods=['POST'])
def start_crawl(model):
    ## TODO Specify model
    ## TODO FIX URL for scale out
    return requests.post("http://sparkler:6000/cmd/crawler/crawl/").text


@mod_app.route('/cmd/crawler/int/<model>', methods=['POST'])
def kill_crawl_gracefully(model):
    ## TODO Specify model
    ## TODO FIX URL for scale out
    return requests.post("http://sparkler:6000/cmd/crawler/int/").text


@mod_app.route('/cmd/crawler/kill/<model>', methods=['POST'])
def force_kill_crawl(model):
    ## TODO Specify model
    ## TODO FIX URL for scale out
    return requests.post("http://sparkler:6000/cmd/crawler/kill/").text


@mod_app.route('/cmd/seed/upload/<model>', methods=['POST'])
def upload_seed(model):
    print request.get_data()

    ## TODO Convert uploaded text to file for sparker.
    ## TODO Come up with a way of updating the uploaded data.
    ## TODO Allow to specify model

    return requests.post("http://sparkler:6000/cmd/seed/upload/", data=request.get_data(),
                         headers={key: value for (key, value) in request.headers if key != 'Host'}).text
