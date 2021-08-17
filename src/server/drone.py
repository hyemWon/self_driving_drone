# import numpy as np
from util.data import Data
import threading
import socket
import time


class DroneServer:
    def __init__(self):
        self.host_name = 'Drone Data Socket Server'
        self.host = '141.223.122.51'
        self.port = 8486
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.data = Data().instance()
        self.lock = self.data.lock

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

                dst_lat, dst_lng, command = 45.0, 45.0, 1

                packet = str(dst_lat) + '/' + str(dst_lng) + '/' + str(command)
                conn.sendall((str(len(packet))).encode().ljust(8) + packet.encode())

                print(lat, lng, dst_lat, dst_lng)
                # TODO : Send to DataQueue Web/APP
                time.sleep(1)

            except Exception as e:
                self.isRun = False
                print(e)
                print("-------- Close {}".format(self.host_name))