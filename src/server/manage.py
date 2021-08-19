from flask import Flask
from realsense import RealSenseServer
from seek_thermal import SeekThermalServer
from drone import DroneServer
from src.server.controller import gmap, user
from util.cleaner import remove_all_img


class ManageServer:
    def __init__(self):
        self.rs_server = RealSenseServer()
        self.seek_thermal_server = SeekThermalServer()
        self.drone_server = DroneServer()

        self.app = Flask(__name__)
        self.app.register_blueprint(gmap.blue_gmap)
        self.app.register_blueprint(user.blue_user)

    def run(self):
        remove_all_img()                # remove rgb/depth/theraml/alphapose image
        self.rs_server.run()            # realsense thread start
        self.seek_thermal_server.run()  # seek_thermal thread start
        self.drone_server.run()         # drone thread start

        self.app.run(host='141.223.122.51', port=50000)


if __name__ == '__main__':
    # run server
    manager = ManageServer()
    manager.run()
