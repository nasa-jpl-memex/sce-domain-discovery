# Import flask and template operators
from flask import Flask
from app.apis import api

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


# Initialize flask-restplus
api.init_app(app)
