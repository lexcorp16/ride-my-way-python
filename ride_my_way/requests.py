import uuid
import sqlite3
from ride_my_way.rides import Ride
from flask_restful import Resource, reqparse
from flask_jwt_extended import (jwt_required, get_jwt_identity)


parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True,
                    help='This field cannot be left blank')


class Requests(Resource):
    @classmethod
    def find_by_id(cls, id):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM requests WHERE id=?"

        result = cursor.execute(query, (id,))
        row = result.fetchone()

        connection.close()

        if row is not None:
            return row
        return None

    @jwt_required
    def post(self, rideId):
        request_data = parser.parse_args()
        current_user = get_jwt_identity()

        ride = Ride.find_by_id(rideId)

        if ride is None:
            return {
                "status": False,
                "message": "Ride not found"
            }, 404
        elif ride[1] == current_user:
            return {
                "status": False,
                "message": "You cannot request a ride you created"
            }, 400

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        request_id = str(uuid.uuid4())
        create_request_query = "INSERT INTO requests(id, ride_id, user_id, name) values(?, ?, ?, ?)"
        cursor.execute(create_request_query, (request_id,
                                              rideId, current_user, request_data["name"]))

        connection.commit()
        connection.close()
        return {
            "status": True,
            "message": "Rides request created!",
        }, 201

    @jwt_required
    def get(self, rideId):
        current_user = get_jwt_identity()

        ride = Ride.find_by_id(rideId)

        if ride is None:
            return {
                "status": False,
                "message": "Ride not found"
            }, 404
        elif ride[1] != current_user:
            return {
                "status": False,
                "message": "You cannot get requests for rides you did not create"
            }, 400

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        requests_query = "SELECT * FROM requests WHERE ride_id=?"
        result = cursor.execute(requests_query, (rideId,)).fetchall()
        requests = []

        for request in result:
            requests.append({
                "id": request[0],
                "ride": request[1],
                "user": request[2],
                "name": request[3],
                "status": request[4]
            })

        connection.close()

        return {
            "status": True,
            "message": "Requests fetched successfully",
            "data": requests
        }


class RespondToRequest(Resource):
    @jwt_required
    def put(self, rideId, requestId):
        current_user = get_jwt_identity()
        request_parser = reqparse.RequestParser()
        request_parser.add_argument('status', type=str, required=True,
                                    help='This field cannot be left blank')

        request_data = request_parser.parse_args()

        ride = Ride.find_by_id(rideId)

        if ride is None:
            return {
                "status": False,
                "message": "Ride not found"
            }, 404
        elif ride[1] != current_user:
            return {
                "status": False,
                "message": "You cannot get update requests for rides you did not create"
            }, 400

        request = Requests.find_by_id(requestId)

        if request is None:
            return {
                "status": False,
                "message": "Request not found"
            }, 404


        if request_data["status"] not in ["A", "P", "R"]:
            return {
                "status": False,
                "message": "Invalid status parameter, must be one of 'A', 'P' or 'R'"
            }, 400

        query = "UPDATE requests SET status=? WHERE ride_id=?"

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute(query, (request_data["status"], rideId))
        connection.commit()
        connection.close()

        return {
            "status": True,
            "message": "Request updated successfully"
        }
