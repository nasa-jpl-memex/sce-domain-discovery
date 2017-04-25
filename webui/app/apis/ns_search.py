from flask_restplus import Namespace, Resource, fields
from app import search
import json

api = Namespace('search', description='Query Duck Duck Go for results')


@api.route('/<query>')
@api.param('query', 'Query string to search')
class Search(Resource):
    @api.doc('search')
    def get(self, query):
        """Search Duck Duck Go"""
        url_details = search.query_and_fetch(query, top_n=12)
        return json.dumps(url_details)
