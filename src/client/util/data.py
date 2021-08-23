from .singleton import Singleton
from threading import Lock


class Data(Singleton):
    def __init__(self):
        self.gps_point = {
            'current': [0.0, 0.0],          # Current drone GPS point
            'base_station': [0.0, 0.0],     # Base Station GPS point
            'src': [0.0, 0.0],              # service start(source) GPS point
            'dst': [0.0, 0.0]               # service end(destination) GPS point
        }

        # Control mode
        self.control_mode = 0

        # is drone action start
        self.drone_is_doing_action = False

        # drone controlling signal
        self.control_information = {

        }

        # thread lock
        self.lock = Lock()


