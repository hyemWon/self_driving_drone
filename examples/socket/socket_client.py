import cv2
import socket
import numpy as np
import threading
import pyrealsense2 as rs
import time


def recvall(sock, count):
    # 바이트 문자열
    buf = b''

    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def realsenseClient():
    name = 'Realsense Camera Client'
    host = '141.223.122.51'
    port = 8485

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    pipeline = rs.pipeline()
    config = rs.config()

    # 1920x1080 - 30, 15, 6 fps / 1280x720 - 60, 30, 15, 6 fps / 960x540 - 60, 30, 15, 6 fps
    width, height, fps = 1280, 720, 30
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)

    pipeline.start(config)
    pipeline.wait_for_frames()  # skip some frames
    cv2.waitKey(10)

    try:
        while True:
            # 비디오의 한 프레임씩 읽는다.
            # st = time.time()
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            # if required depth frame

            # depth_frame = frames.get_depth_frame()
            if not color_frame:
                print('Skipped Frame')
                continue

            # convert numpy array
            data = np.asanyarray(color_frame.get_data())

            # encoding data
            res, encode_frame = cv2.imencode('.jpg', data, encode_param)
            string_data = np.array(encode_frame).tostring()

            # send to server
            # (str(len(stringData))).encode().ljust(16) --> data length(header) + real data
            s.sendall((str(len(string_data))).encode().ljust(8) + string_data)

            # TODO : color_frame + depth_frame
            # data = np.asanyarray(color_frame.get_data())
            # res, frame = cv2.imencode('.jpg', data, encode_param)
            # string_data = np.array(frame).tostring()
            # s.sendall((str(len(string_data))).encode().ljust(8) + string_data)

            # print(name, frames.get_frame_number(), time.time() - st)
            cv2.waitKey(1)

    except Exception as e:
        print("#### close {}".format(name))
        print(e)


def droneClient():
    name = 'Drone Client'
    host = '141.223.122.51'
    port = 8486

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    lat, lng = 1.0, 1.0

    try:
        while True:
            # 비디오의 한 프레임씩 읽는다.
            # st = time.time()
            # TODO : other control signal added
            packet = str(lat) + '/' + str(lng)
            # (str(len(stringData))).encode().ljust(16) --> data length(header) + real data
            s.sendall((str(len(packet))).encode().ljust(8) + packet.encode())
            # sendCheck = s.recv()

            cv2.waitKey(100)    # 0.1s interval
            # print(name, time.time() - st)

    except Exception as e:
        print("### close {}".format(name))
        print(e)


if __name__ == '__main__':
    thread_rs_client = threading.Thread(target=realsenseClient)
    thread_drone_client = threading.Thread(target=droneClient)

    thread_rs_client.start()
    thread_drone_client.start()
