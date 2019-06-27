from ride_my_way import api
from ride_my_way.user import RegisterUser, LoginUser
from ride_my_way.rides import Rides, Ride
from ride_my_way.requests import Requests, RespondToRequest

api.add_resource(RegisterUser, '/signup')
api.add_resource(LoginUser, '/login')
api.add_resource(Rides, '/rides')
api.add_resource(Ride, '/ride/<string:id>')
api.add_resource(Requests, '/rides/<string:rideId>/requests')
api.add_resource(RespondToRequest, '/rides/<string:rideId>/requests/<string:requestId>')