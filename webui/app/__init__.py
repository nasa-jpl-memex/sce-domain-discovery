# Import flask and template operators
from flask import Flask
from app.apis import api

from sklearn.externals import joblib
import os

# Define the WSGI application object
app = Flask(__name__,
            static_url_path='',
            static_folder='static')




# Configurations
app.config.from_object('config')


# Import a module / component using its blueprint handler variable
from app.controller import mod_app as app_module


# Register blueprint(s)
app.register_blueprint(app_module)

#filename = 'model.pkl'
#if os.path.isfile(filename):
#    model = joblib.load(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
#    setattr(app, 'model', model)

# Initialize flask-restplus
api.init_app(app)
