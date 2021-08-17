import pyrealsense2 as rs
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

        self.pipeline = rs.pipeline()
        self.config = rs.config()

        self.wrapper = rs.pipeline_wrapper(self.pipeline)
        self.profile = self.config.resolve(self.wrapper)
        self.device = self.profile.get_device()
        self.device_name = str(self.device.get_info(rs.camera_info.product_line))

        self.isRun = False

    def run(self):
        # 1920x1080 - 30, 15, 6 fps / 1280x720 - 60, 30, 15, 6 fps / 960x540 - 60, 30, 15, 6 fps
        width, height, fps = 960, 540, 15
        # self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)

        self.pipeline.start(self.config)
        self.pipeline.wait_for_frames()

        self.isRun = True
        t = threading.Thread(target=self.thread)
        t.daemon = True
        t.start()

    def thread(self):
        print("-------- {} start".format(self.host_name))
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

        self.sock.connect((self.host, self.port))

        time.sleep(0.001)
        while self.isRun:
            try:
                st = time.time()
                frames = self.pipeline.wait_for_frames()  # get frame
                # depth_frame = frames.get_depth_frame()  # get depth frame from frames
                color_frame = frames.get_color_frame()  # get rgb frame from frames

                # if not depth_frame or not color_frame:
                #     continue

                # convert numpy array
                data = np.asanyarray(color_frame.get_data())

                res, encode_frame = cv2.imencode('.jpg', data, encode_param)
                string_data = np.array(encode_frame).tostring()

                self.sock.sendall((str(len(string_data))).encode().ljust(8) + string_data)

                # TODO : depth_frame
                # data = np.asanyarray(color_frame.get_data())
                # res, frame = cv2.imencode('.jpg', data, encode_param)
                # string_data = np.array(frame).tostring()
                # s.sendall((str(len(string_data))).encode().ljust(8) + string_data)

                time.sleep(0.01)

                print('#RS# realsense job finished {}'.format(time.time() - st))

            except Exception as e:
                self.isRun = False
                print(e)
                print("-------- Close {}".format(self.host_name))