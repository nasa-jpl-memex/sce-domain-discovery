from flask import Blueprint, request, render_template, redirect, url_for, send_from_directory
from app import classifier
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
