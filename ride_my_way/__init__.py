from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
api = Api(app)
jwt = JWTManager(app)

@app.route("/")
def index():
    return jsonify({'message': 'Hello, World!'})