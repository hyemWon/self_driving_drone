from .singleton import Singleton
from threading import Lock
from collections import deque


class Data(Singleton):
    def __init__(self):
        self.lat_drone = 0.0
        self.lng_drone = 0.0

        self.control_mode = 0

        self.lat_dst = 0.0
        self.lng_dst = 0.0

        self.lock = Lock()


class DataQueue(Singleton):
    def __init__(self):
        self.queue = deque()
        self.lock = Lock()

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
