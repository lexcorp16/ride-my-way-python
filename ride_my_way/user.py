import sqlite3
import uuid
from flask_restful import Resource, reqparse
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token


class User:
    def __init__(self, _id, username, password):
        self.id = _id
        self.username = username
        self.password = password

    @classmethod
    def find_by_username(cls, username):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE username=?"
        result = cursor.execute(query, (username,))

        row = result.fetchone()

        if row is not None:
            user = cls(*row)
        else:
            user = None

        connection.close()
        return user

    @classmethod
    def find_user(cls, param):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE {}=?".format(param['name'])
        result = cursor.execute(query, (param['value'],))

        row = result.fetchone()

        if row is not None:
            user = cls(*row)
        else:
            user = None

        connection.close()
        return user


parser = reqparse.RequestParser()
parser.add_argument('username', type=str, required=True,
                    help='This field cannot be left blank')
parser.add_argument('password', type=str, required=True,
                    help='This field cannot be left blank')


class RegisterUser(Resource):
    def post(self):
        request_data = parser.parse_args()
        params = {
            'name': 'username',
            'value': request_data['username']
        }
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        if User.find_user(params) is not None:
            return {"message": "A user already exists with that username"}, 400

        else:
            user_id = str(uuid.uuid4())
            query = "INSERT INTO users VALUES (?, ?, ?)"
            hashed_password = pbkdf2_sha256.hash(request_data['password'])
            access_token = create_access_token(
                identity=user_id)
            cursor.execute(
                query, (user_id, request_data['username'], hashed_password))
            connection.commit()
            connection.close()

            return {"status": True, "message": "Sign up successful!", "data": {
                "username": request_data['username'],
                "password": hashed_password,
                "access_token": access_token
            }}, 201


class LoginUser(Resource):
    def post(self):
        print('starting')
        request_data = parser.parse_args()
        params = {
            'name': 'username',
            'value': request_data['username']
        }

        user = User.find_user(params)

        if user is None:
            return {"message": "No user exists with that username"}, 400

        else:
            password_valid = pbkdf2_sha256.verify(
                request_data['password'], user.password)

            if password_valid:
                access_token = create_access_token(
                    identity=user.id)
                return {
                    "status": True,
                    "message": "Login successful!",
                    "data": {
                        "username": user.username,
                        "access_token": access_token
                    }
                }, 200

            else:
                return {
                    "status": False,
                    "message": "Invalid credentials",
                }, 400
