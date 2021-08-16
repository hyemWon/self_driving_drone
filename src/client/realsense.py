import pyrealsense2 as ps
import numpy as np
import threading
import socket
import cv2
import time


class RealSenseClient:
    def __init__(self):
        self.host_name = 'Realsense Camera Socket Client'
        self.host = '141.223.122.51'
        self.port = 8485
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.isRun = False

    def run(self):
        self.isRun = True
        t = threading.Thread(target=self.thread)
        t.daemon = True
        t.start()

    def thread(self):
        print("-------- {} start".format(self.host_name))
        encode_frame = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

        self.sock.connect((self.host, self.port))

        time.sleep(0.001)
        while self.isRun:
            try:
                while True:
                    time.sleep(0.001)

            except Exception as e:
                self.isRun = False
                print(e)
                print("-------- Close {}".format(self.host_name))