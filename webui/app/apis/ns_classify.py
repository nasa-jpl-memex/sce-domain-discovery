from flask_restplus import Namespace, Resource
from flask import request
from app import classifier
import json
api = Namespace('classify', description='Interact with the ML model')


@api.route('/predict', methods=['GET','POST'])
class Predict(Resource):
    @api.doc('predict')
    def get(self, content, model):
        """Predict using ML model"""
        classes = {
            -1: 'Model doesn\'t exist',
            0: 'Not Relevant',
            1: 'Relevant',
            2: 'Highly Relevant'
        }
        args = request.args
        print (args)
        if len(args) != 0:
            content = args['content']
        result = classifier.predict(model, content)
        return classes[result]

    @api.doc('predict')
    def post(self):
        """Predict using ML model"""
        classes = {
            -1: 'Model doesn\'t exist',
            0: 'Not Relevant',
            1: 'Relevant',
            2: 'Highly Relevant'
        }
        result = -1
        data = request.data
        print ("request data"+ data)
        d = json.loads(data)
        if len(data) != 0:
            content = d['score'][0]['content']
            model = d['score'][0]['model']
            result = classifier.predict(model, content)
        return classes[result]
