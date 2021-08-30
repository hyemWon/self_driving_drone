import numpy as np
import cv2
import threading
import socket
import time
from util.data import FrameQueue


class RealSenseServer:
    def __init__(self):
        self.host_name = 'Realsense Camera Socket Server'
        self.host = '141.223.122.51'
        self.port = 8485
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.frame_queue = FrameQueue().instance()
        self.isRun = False

    def run(self):
        t = threading.Thread(target=self.thread)
        t.daemon = True
        self.isRun = True
        t.start()

    def thread(self):
        print(f"-------- {self.host_name} start")
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)
        conn, addr = self.sock.accept()

        while self.isRun:
            try:
                st = time.time()

                length = self.recvall(conn, 8)                      # Receive packet length
                stringData = self.recvall(conn, int(length))        # receive real data
                data = np.fromstring(stringData, dtype='uint8')     # convert to numpy array

                frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
                self.frame_queue.push(frame)

                # print("#RS# process finished {}".format(time.time() - st))

            except Exception as e:
                self.isRun = False
                print(e)
                print("-------- Close {}".format(self.host_name))

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf