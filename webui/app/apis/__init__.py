from flask_restplus import Api

from app.apis.ns_search import api as search_api

api = Api(title='Seed Generation', version='1.0', description='Tool to generate seeds for Domain Discovery')

api.add_namespace(search_api)