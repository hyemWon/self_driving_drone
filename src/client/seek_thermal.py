from util.seekpro import SeekPro
import numpy as np
import threading
import socket
import cv2
import time


class SeekThermalClient:
    def __init__(self):
        self.host_name = 'Seek Theraml Camera Socket Client'
        self.host = '141.223.122.51'
        self.port = 8487
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.cam = SeekPro()

        self.isRun = False

    def run(self):
        self.isRun = True
        t = threading.Thread(target=self.thread)
        t.daemon = True
        t.start()

    def thread(self):
        print("-------- {} start".format(self.host_name))
        self.sock.connect((self.host, self.port))

        encode_frame = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

        time.sleep(0.001)
        while self.isRun:
            try:
                while True:
                    st = time.time()
                    frame = self.cam.get_image()
                    rescale_frame = self.cam.rescale(frame)
                    res, encode_frame = cv2.imencode('.jpg', rescale_frame, encode_frame)
                    string_data = np.array(encode_frame).tostring()

                    self.sock.sendall((str(len(string_data))).encode().ljust(8) + string_data)
                    time.sleep(0.001)

                    print('#ST# seek thermal job finished {}'.format(time.time() - st))

            except Exception as e:
                self.isRun = False
                print(e)
                print("-------- Close {}".format(self.host_name))
