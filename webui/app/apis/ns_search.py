from flask_restplus import Namespace, Resource, fields, cors

from app import search
import json

from pyArango.theExceptions import DocumentNotFoundError
from werkzeug.exceptions import BadRequest

api = Namespace('search', description='Query Duck Duck Go for results')


@api.route('/<model>/<query>')
@api.param('query', 'Query string to search')
class Search(Resource):
    @api.doc('search')
    @cors.crossdomain(origin='*')
    def get(self, model, query):
        """Search Duck Duck Go"""
        try:
            url_details = search.query_and_fetch(query, model, top_n=12)
        except DocumentNotFoundError as e:
            print(e)
            raise BadRequest('Model Not Found')

        return json.dumps(url_details)


