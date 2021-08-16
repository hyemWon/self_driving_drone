from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
from util.data import Data
from threading import Thread, Lock
import asyncio
import socket
import subprocess
import time


class DroneClient:
    def __init__(self):
        self.host_name = 'Drone Data Socket Client'
        self.host = '141.223.122.51'
        self.port = 8486
        self.address = './mavsdk_server -p 50051 serial:///dev/ttyTHS1:921600'
        self.script_path = '~/self_driving_drone/scripts/'

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.data = Data().instance()
        self.lock = Lock()

        self.isRunSocket = False
        self.isRunDrone = False
        self.cnt = 0    # cnt for test

    def run(self):
        self.isRunSocket = True
        # sending data to server
        ts = Thread(target=self.thread_socket)
        ts.daemon = True

        self.isRunDrone = True
        # drone controlling thread
        td = Thread(target=self.thread_drone)
        td.daemon = True

        ts.start()
        td.start()

    def thread_socket(self):
        print("-------- {} start".format(self.host_name))
        self.sock.connect((self.host, self.port))

        time.sleep(0.001)
        while self.isRunSocket:
            try:
                st = time.time()
                # get data for server
                self.lock.acquire()
                lat_drone = self.data.lat_drone
                lng_drone = self.data.lng_drone
                self.lock.release()

                # send drone data to server
                packet_send = str(lat_drone) + '/' + str(lng_drone)

                print('#D.S# sending drone data to server')
                self.sock.sendall((str(len(packet_send))).encode().ljust(8) + packet_send.encode())

                # recv app data from server
                print('#D.S# receiving drone data from server')
                header = self.sock.recv(8)
                packet_recv = self.recvall(len(header))
                lat_dst, lng_dst, control_mode = packet_recv.decode(encoding='utf-8').split(sep='/')

                self.lock.acquire()
                self.data.lat_dst = lat_dst
                self.data.lng_dst = lng_dst
                self.lock.release()

                time.sleep(1)
                print('#D.S# process finished {}'.format(self.host_name, time.time() - st))
            except Exception as e:
                self.isRunSocket = False
                print(e)
                print("-------- Close {}".format(self.host_name))

    def thread_drone(self):
        while self.isRunDrone:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                print('### Drone action start')
                loop.run_until_complete(self.drone_action())
                print('### Drone action finished')
                loop.close()
            except Exception as e:
                self.isRunDrone = False
                print(e)
                print("-------- Close {}".format(self.host_name))

    async def drone_action(self):
        st = time.time()

        self.lock.acquire()
        self.data.lng_dst += 1
        lng = self.data.lng_drone

        self.data.lat_drone += 1
        lat = self.data.lat_drone

        dst_lat = self.data.lat_dst
        dst_lng = self.data.lng_dst
        self.lock.release()

        await asyncio.sleep(1)

        print('#D.D# drone action finished {}'.format(time.time() - st))

        # drone = System(mavsdk_server_address='localhost', port=50051)
        # await drone.connect(system_address='serial:///dev/ttyTHS1:921600')
        #
        # print("Waiting for drone to connect...")
        # async for state in drone.core.connection_state():
        #     if state.is_connected:
        #         print("Drone discovered")
        #         break
        #
        # print("Waiting for drone to have a global position estimate...")
        # async for health in drone.telemetry.health():
        #     ### 센서들의 상태 캘리브래이션 확인
        #     ### position 제어에 충분한지 확인
        #     if health.is_global_position_ok:
        #         print("Global position estimate ok")
        #         ### 제어에 충분하다면 출력
        #         break
        #
        # print("Fetching amsl altitude at home location....")
        # async for terrain_info in drone.telemetry.home():
        #     absolute_altitude = terrain_info.absolute_altitude_m
        #     break
        #
        # print("-- Arming")
        # await drone.action.arm()
        # ### 이륙을 하지 않고 드론의 구동이 시작
        # ### 프로펠러가 돌기 시작함
        # flying_alt = 2.0
        # await drone.action.set_takeoff_altitude(flying_alt)
        # ### 이륙하면 도달한 드론의 고도를 절대고도+30으로 맞춤
        # await asyncio.sleep(10)
        # ### 위의 코드들을 실행하고 2초 정도 다른 명령을 주진 않음
        #
        # print("-- disarming --")
        # await drone.action.disarm()
        # await asyncio.sleep(10)

    def open_pixhawk_server(self):
        print("----OpenServer Thread Start")
        subprocess.run('bash ~/self-driving-drone/scripts/run_mavsdk_server.sh', shell=True)
        print("----Server Start!----")
        print("#############################################################################")

    def recvall(self, count):
        # 바이트 문자열
        buf = b''
        while count:
            newbuf = self.sock.recv(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    # def packet_parser(self, packet):
    #     data = packet.split('/')
    #
    #     return

