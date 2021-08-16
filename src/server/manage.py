from flask import Flask
from realsense import RealSenseServer
from seek_thermal import SeekThermalServer
from drone import DroneServer
from src.server.controller import gmap, user


class ManageServer:
    def __init__(self):
        self.rs_server = RealSenseServer()
        self.seek_thermal_server = SeekThermalServer()
        self.drone_server = DroneServer()
        # TODO : add flask
        self.app = Flask(__name__)
        self.app.register_blueprint(gmap.blue_gmap)
        self.app.register_blueprint(user.blue_user)

    def run(self):
        self.rs_server.run()
        self.seek_thermal_server.run()
        self.drone_server.run()

        self.app.run(host='141.223.122.51', port=50000)


if __name__ == '__main__':
    # run server
    manager = ManageServer()
    manager.run()
