import socket
import threading
import cv2
import numpy as np
# import time


# socket에서 수신한 버퍼를 반환하는 함수
def recvall(sock, count):
    # 바이트 문자열
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf


# --------- realsense camera socket server thread
def realsenseServer():
    name = 'Realsense Image Server'
    host = '141.223.122.51'
    port = 8485
    print('{} : {}, {}'.format(name, host, port))

    realsense_server_flag = True

    # TCP socket 사용
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    # 서버의 아이피와 포트번호 지정
    s.bind((host, port))
    print('Socket bind complete')
    # 클라이언트의 접속을 기다린다. (클라이언트 연결을 10개까지 받는다)
    s.listen(10)
    print('Socket now listening')

    # 연결, conn에는 소켓 객체, addr은 소켓에 바인드 된 주소
    conn, addr = s.accept()
    print(addr)

    # cv2.namedWindow('ImageWindow')
    frame_cnt = 0
    while realsense_server_flag:
        try:
            print("Start Receiving Frame")
            # st = time.time()
            # client에서 받은 stringData의 크기 (==(str(len(stringData))).encode().ljust(16))
            length = recvall(conn, 8)
            print(int(length), end=' ')
            stringData = recvall(conn, int(length))
            data = np.fromstring(stringData, dtype='uint8')
            # data = np.asanyarray(data)
            print(data.dtype, end=' ')
            # data를 디코딩
            # frame = data.reshape((540, 960, 3))

            frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
            cv2.imshow('Frame', frame)
            # cv2.imwrite('../Images/frame{}.jpg'.format(frame_cnt), frame)
            frame_cnt += 1
            # print(name, ':', time.time() - st)
            cv2.waitKey(1)

        except Exception as e:
            realsense_server_flag = False
            print(e)
            print("-------- Close {}".format(name))


# --- drone data socket server
def droneServer():
    name = 'Drone Data Server'
    host = '141.223.122.51'
    port = 8486
    print('{} : {}, {}'.format(name, host, port))

    drone_server_flag = True

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    s.bind((host, port))
    print('Socket bind complete')

    s.listen(10)
    print('Socket now listening')

    conn, addr = s.accept()
    print("Connected IP : {}".format(addr))

    lat, lng = 0.0, 0.0

    while drone_server_flag:
        try:
            print("Start Receiving Drone Data Packet")
            # st = time.time()
            header = conn.recv(8)
            packet = conn.recv(int(header))

            if not packet:
                print("{} packet not received !!".format(name))
                continue

            # TODO : other control signals added
            lat, lng = packet.decode(encoding='utf-8').split(sep='/')
            print(lat, lng)

            # print(name, ':', time.time() - st)

        except Exception as e:
            drone_server_flag = False
            print(e)
            print("-------- Close {}".format(name))


if __name__ == '__main__':
    thread_rs_server = threading.Thread(target=realsenseServer)
    thread_data_server = threading.Thread(target=droneServer)

    # TODO : thread daemonize
    # thread_rs_server.daemon = True
    # thread_data_server.daemon = True

    thread_rs_server.start()
    thread_data_server.start()


