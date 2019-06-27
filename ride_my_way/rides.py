import uuid
import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt_extended import (jwt_required, get_jwt_identity)


parser = reqparse.RequestParser()
parser.add_argument('destination', type=str, required=True,
                    help='This field cannot be left blank')
parser.add_argument('point_of_departure', type=str, required=True,
                    help='This field cannot be left blank')
parser.add_argument('vehicle_capacity', type=str, required=True,
                    help='This field cannot be left blank')
parser.add_argument('departure_time', type=str, required=True,
                    help='This field cannot be left blank')
parser.add_argument('departure_date', type=str, required=True,
                    help='This field cannot be left blank')


class Ride(Resource):
    @classmethod
    def find_by_id(cls, id):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM rides WHERE id=?"

        result = cursor.execute(query, (id,))
        row = result.fetchone()

        connection.close()

        if row is not None:
            return row
        return None

    @classmethod
    def update(cls, ride):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        create_ride_query = "UPDATE rides SET destination=?, point_of_departure=?, vehicle_capacity=?, departure_time=?, departure_date=? WHERE id=?"

        cursor.execute(create_ride_query, (ride['destination'], ride['point_of_departure'],
                                           ride['vehicle_capacity'], ride['departure_time'], ride['departure_date'], ride['id']))

        connection.commit()
        connection.close()
        return 'done'

    def get(self, id):
        try:
            ride = Ride.find_by_id(id)
        except:
            return {
                "status": False,
                "message": "An error occured fetching the ride"
            }, 500

        if ride is None:
            return {
                "status": False,
                "message": "Ride not found!"
            }, 400

        return {
            "status": True,
            "message": "Ride retrieved!",
            "data": {
                "id": ride[0],
                "user": ride[1],
                "destination": ride[2],
                "point_of_departure": ride[3],
                "vehicle_capacity": ride[4],
                "departure_time": ride[5],
                "departure_date": ride[6]
            }
        }

    @jwt_required
    def put(self, id):
        current_user = get_jwt_identity()
        request_data = parser.parse_args()

        ride = self.find_by_id(id)
        updated_item = {
            'id': id,
            "user": current_user,
            "destination": request_data['destination'],
            "point_of_departure": request_data['point_of_departure'],
            "vehicle_capacity": request_data['vehicle_capacity'],
            "departure_time": request_data['departure_time'],
            "departure_date": request_data['departure_date']
        }

        if ride is None:
            return {
                "status": False,
                "message": "Ride not found!"
            }, 400

        if ride[1] != current_user:
            return {
                "status": False,
                "message": "You cannot update a ride you did not create"
            }, 401

        try:
            Ride.update(updated_item)
            return {
                "status": True,
                "message": "Ride offer updated successfully",
                "data": updated_item
            }, 200
        except:
            return {
                "status": False,
                "message": "An error occured updating the ride"
            }, 500


class Rides(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = 'SELECT * FROM rides'
        result = cursor.execute(query)

        rows = result.fetchall()
        connection.close()
        rides = []

        for ride in rows:
            rides.append({
                "id": ride[0],
                "user": ride[1],
                "destination": ride[2],
                "point_of_departure": ride[3],
                "vehicle_capacity": ride[4],
                "departure_time": ride[5],
                "departure_date": ride[6]
            })
        return {
            "status": True,
            "message": "Rides fetched successfully!",
            "data": rides
        }

    @jwt_required
    def post(self):
        current_user = get_jwt_identity()
        request_data = parser.parse_args()

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        existing_rides_query = "SELECT * FROM rides WHERE user_id=? AND departure_time=? AND departure_date=?"
        existing_rides = cursor.execute(existing_rides_query, (
            current_user, request_data['departure_time'], request_data['departure_date']))

        if len(existing_rides.fetchall()) > 0:
            connection.close()
            return {
                "status": False,
                "message": 'You already have a ride scheduled for this period.',
            }, 400

        ride_id = str(uuid.uuid4())
        create_ride_query = "INSERT INTO rides(id, user_id, destination, point_of_departure, vehicle_capacity, departure_time, departure_date) values(?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(create_ride_query, (ride_id, current_user, request_data['destination'], request_data[
                       'point_of_departure'], request_data['vehicle_capacity'], request_data['departure_time'], request_data['departure_date']))

        connection.commit()
        connection.close()
        return {
            "status": True,
            "message": "Ride offer created successfully",
            "data": {
                "id": ride_id,
                "user": current_user,
                "destination": request_data['destination'],
                "point_of_departure": request_data['point_of_departure'],
                "vehicle_capacity": request_data['vehicle_capacity'],
                "departure_time": request_data['departure_time'],
                "departure_date": request_data['departure_date']
            }
        }, 201
