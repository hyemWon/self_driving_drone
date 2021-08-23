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
                command = -1

                self.lock.acquire()
                # save current drone gps point
                self.data.gps_point['current'][0], self.data.gps_point['current'][1] = lat, lng

                dst_lat, dst_lng = self.data.gps_point['dst'][0], self.data.gps_point['dst'][1]
                if self.data.control_mode != -1:
                    command = self.data.control_mode
                self.lock.release()

                # Send to Drone(Client) destination gps, control mode
                packet = str(dst_lat) + '/' + str(dst_lng) + '/' + str(command)
                conn.sendall((str(len(packet))).encode().ljust(8) + packet.encode())

                time.sleep(1)

            except Exception as e:
                self.isRun = False
                print(e)
                print("-------- Close {}".format(self.host_name))