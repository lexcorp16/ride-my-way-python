import sqlite3

connection = sqlite3.connect('data.db')

cursor = connection.cursor()

create_users_table = "CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT, password TEXT)"
create_rides_table = "CREATE TABLE IF NOT EXISTS rides (id TEXT PRIMARY KEY, user_id TEXT REFERENCES users(id), destination text not null, point_of_departure text not null, vehicle_capacity SMALLINT not null, departure_time TEXT not null, departure_date TEXT not null)"
create_requests_table = "CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, ride_id TEXT REFERENCES rides(id), user_id TEXT REFERENCES users(id) not null, name TEXT not null, status TEXT CHECK( status IN ('P','R','A') )  DEFAULT 'P')"

cursor.execute(create_users_table)
cursor.execute(create_rides_table)
cursor.execute(create_requests_table)

connection.commit()
connection.close()
