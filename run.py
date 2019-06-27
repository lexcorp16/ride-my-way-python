from ride_my_way import app
import ride_my_way.models
import ride_my_way.views

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

