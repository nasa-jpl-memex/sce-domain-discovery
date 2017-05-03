from flask_restplus import Namespace, Resource
from flask import request
from app import classifier

api = Namespace('classify', description='Interact with the ML model')


@api.route('/predict/<content>', methods=['GET','POST'])
class Predict(Resource):
    @api.doc('predict')
    def get(self, content):
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
        result = classifier.predict(content)
        return classes[result]
