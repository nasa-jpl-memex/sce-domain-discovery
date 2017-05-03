from flask_restplus import Api

from app.apis.ns_search import api as search_api
from app.apis.ns_classify import api as classify_api

api = Api(title='Seed Generation', version='1.0', description='Tool to generate seeds for Domain Discovery')

api.add_namespace(search_api)
api.add_namespace(classify_api)