from .singleton import Singleton
from threading import Lock


class Data(Singleton):
    def __init__(self):
        self.lat_drone = 0.0
        self.lng_drone = 0.0

        self.control_mode = 0
        self.drone_is_run = False

        self.lat_dst = 0.0
        self.lng_dst = 0.0

        self.lock = Lock()


