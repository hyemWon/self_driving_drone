from src.server.util.singleton import Singleton
from threading import Lock
from collections import deque


class DataQueue(Singleton):
    def __init__(self):
        self.queue = deque()
        self.lock = Lock()


class DataCollector:    # class DataCollector(Singleton):
    def __init__(self):
        self.queue = []
        self.lock = Lock()


if __name__ == '__main__':
    # if use same collector
    # instance_name = DataCollector().instance()
    drone_state_collector = DataCollector()
    image_frame_collector = DataQueue().instance()
    data_frame_collector = DataQueue().instance()
    print(drone_state_collector)
    print(image_frame_collector)
    print(data_frame_collector)
