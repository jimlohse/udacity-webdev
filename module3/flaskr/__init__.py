from flask import Flask, json, jsonify
from models import setup_db, Plant
from flask_cors import CORS, cross_origin

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    #CORS(app)
    CORS(app, resources={r"*/api/*" : {origins: '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
        return response

    @app.route('/')
    @cross_origin
    def hello():
        return jsonify({'message':'Hello Whirled'})

    @app.route('/smiley')
    def smiley():
        return ':)'
    
    return app