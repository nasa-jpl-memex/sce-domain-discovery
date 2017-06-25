from flask import Blueprint, request, render_template, redirect, url_for, send_from_directory
from app import classifier
import requests
import os

# Define Blueprint(s)
mod_app = Blueprint('application', __name__, url_prefix='/explorer')


# Define Controller(s)
@mod_app.route('/')
def index():
    return send_from_directory('static/pages', 'index.html')

@mod_app.route('/classify/createnew/', methods=['GET'])
def create_new_model():
    return classifier.clear_model()


# POST Requests
@mod_app.route('/classify/update/', methods=['POST'])
def build_model():
    annotations = []
    data = request.get_data()
    for item in data.split('&'):
        annotations.append(int(item.split('=')[1]))
    accuracy = classifier.update_model(annotations)
    return accuracy


@mod_app.route('/classify/upload/', methods=['POST'])
def upload_model():
    return classifier.import_model()


@mod_app.route('/classify/download/', methods=['POST'])
def download_model():
    return classifier.export_model()


@mod_app.route('/classify/exist/', methods=['POST'])
def check_model():
    return classifier.check_model()


@mod_app.route('/cmd/crawler/exist/', methods=['POST'])
def check_crawl_exists():
    return requests.post("http://0.0.0.0:6000/cmd/crawler/exist/").text


@mod_app.route('/cmd/crawler/crawl/', methods=['POST'])
def start_crawl():
    return requests.post("http://0.0.0.0:6000/cmd/crawler/crawl/").text


@mod_app.route('/cmd/crawler/int/', methods=['POST'])
def kill_crawl_gracefully():
    return requests.post("http://0.0.0.0:6000/cmd/crawler/int/").text


@mod_app.route('/cmd/crawler/kill/', methods=['POST'])
def force_kill_crawl():
    return requests.post("http://0.0.0.0:6000/cmd/crawler/kill/").text


@mod_app.route('/cmd/seed/upload/', methods=['POST'])
def upload_seed():
    print request.get_data()
    return requests.post("http://0.0.0.0:6000/cmd/seed/upload/", data=request.get_data(),
                         headers={key: value for (key, value) in request.headers if key != 'Host'}).text
