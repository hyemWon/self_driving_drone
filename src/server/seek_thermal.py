import socket
import threading
import numpy as np
import cv2
import time


class SeekThermalServer:
    def __init__(self):
        self.host_name = 'Seek-Thermal Camera Socket Server'
        self.host = '141.223.122.51'
        self.port = 8487
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.isRun = False

    def run(self):
        t = threading.Thread(target=self.thread)
        t.daemon = True
        self.isRun = True
        t.start()

    def thread(self):
        print("-------- {}".format(self.host_name))
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)
        conn, addr = self.sock.accept()

        cnt = 0
        while self.isRun:
            try:
                st = time.time()
                # client에서 받은 stringData의 크기 (==(str(len(stringData))).encode().ljust(16))
                length = self.recvall(conn, 8)                      # Receive packet length
                stringData = self.recvall(conn, int(length))        # receive real data
                data = np.fromstring(stringData, dtype='uint8')     # convert to numpy array

                frame = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)

                # TODO: Send to Data Queue

                cv2.imwrite("imgs/thermal/frame_{}.jpg".format(cnt), frame)
                cv2.waitKey(10)
                cnt += 1
                print("#ST# process finished {}".format(time.time() - st))

            except Exception as e:
                self.isRun = False
                cv2.destroyAllWindows()
                print(e)
                print("-------- Close {}".format(self.host_name))

    def recvall(self, sock, count):
        # 바이트 문자열
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

