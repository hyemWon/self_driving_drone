from .singleton import Singleton
from multiprocessing import Value, Array, Lock
from collections import deque
import threading


class Data(Singleton):
    def __init__(self):
        # set gps points [lat, lng]
        self.gps_point = {
            'current': [0.0, 0.0],  # Current drone GPS point
            'base_station': [0.0, 0.0],  # Base Station GPS point
            'src': [0.0, 0.0],  # service start(source) GPS point
            'dst': [0.0, 0.0]  # service end(destination) GPS point
        }

        # drone control mode
        self.control_mode = 0
        self.pose = None

        # User certification
        self.is_pass_certification = False
        
        # yolo detection person boxes
        self.person_boxes = {
            # [x, y] / left-up / right-up / left-down / right-down / center-point
            'person': [[0, 0], [0, 1], [1, 0], [1, 1], [0.5, 0.5]]
        }

        # drone controlling signal
        self.control_information = [0, 0, 0, 0]

        # thread lock
        self.lock = threading.Lock()


class FrameQueue(Singleton):
    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()

    def push(self, data):
        self.lock.acquire()
        self.queue.append(data)
        self.lock.release()

    def pop(self):
        if len(self.queue) == 0:
            return None

        self.lock.acquire()
        data = self.queue.pop()
        self.lock.release()

        return data
