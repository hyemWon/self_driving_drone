# import numpy as np
import threading
import socket
from cv2 import waitKey
from time import time


class DroneServer:
    def __init__(self):
        self.host_name = 'Drone Data Socket Server'
        self.host = '141.223.122.51'
        self.port = 8486
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.isRun = False

    def run(self):
        # depth setting
        self.isRun = True
        t = threading.Thread(target=self.thread)
        t.daemon = True
        t.start()

    def thread(self):
        print("-------- {}".format(self.host_name))
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)
        conn, addr = self.sock.accept()

        while self.isRun:
            try:
                header = conn.recv(8)
                packet = conn.recv(int(header))

                if not packet:
                    print("{} packet not received !!".format(self.host_name))
                    continue
                lat, lng = packet.decode(encoding='utf-8').split(sep='/')
                print(lat, lng)

                # TODO : Send to DataQueue Web/APP


                waitKey(100)


            except Exception as e:
                self.isRun = False
                print(e)
                print("-------- Close {}".format(self.host_name))