from .singleton import Singleton
from threading import Lock
from collections import deque


class DataQueue(Singleton):
    def __init__(self):
        self.queue = deque()
        self.lock = Lock()


class DataCollector:
    def __init__(self):
        self.queue = []
        self.lock = Lock()

