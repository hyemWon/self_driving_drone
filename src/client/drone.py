from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
from util.data import Data
import threading
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
        self.lock = self.data.lock

        self.isRunSocket = False
        self.isRunDrone = False
        self.cnt = 0    # cnt for test

    def run(self):
        # open mavsdk server
        tm = threading.Thread(target=self.open_pixhawk_server)
        tm.daemon = True

        self.isRunSocket = True
        # sending data to server
        ts = threading.Thread(target=self.thread_socket)
        ts.daemon = True

        self.isRunDrone = True
        # drone controlling thread
        td = threading.Thread(target=self.thread_drone)

        tm.start()
        time.sleep(1)
        ts.start()
        time.sleep(0.001)
        td.start()
        time.sleep(0.001)

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

                # print('#D.S# sending drone data to server')
                self.sock.sendall((str(len(packet_send))).encode().ljust(8) + packet_send.encode())

                # recv app data from server
                # print('#D.S# receiving drone data from server')
                header = self.recvall(8)
                packet_recv = self.recvall(int(header))
                lat_dst, lng_dst, control_mode = packet_recv.decode(encoding='utf-8').split(sep='/')

                self.lock.acquire()
                self.data.lat_dst = float(lat_dst)
                self.data.lng_dst = float(lng_dst)
                self.data.control_mode = int(control_mode)
                self.lock.release()

                time.sleep(1)
                print('#D.S# socket job finished {}'.format(self.host_name, time.time() - st))

            except Exception as e:
                self.isRunSocket = False
                print(e)
                print(f"-------- Close {self.host_name}")

    def thread_drone(self):
        while self.isRunDrone:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.drone_action())
                loop.close()
            except Exception as e:
                self.isRunDrone = False
                print(e)
                print(f"-------- Close {self.host_name}")

    async def drone_check(self):
        await asyncio.sleep(1)

        drone = System(mavsdk_server_address='localhost', port=50051)
        await drone.connect(system_address='serial:///dev/ttyTHS1:921600')

        print("Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print("Drone discovered")
                break

        print("Waiting for drone to have a global position estimate...")
        async for health in drone.telemetry.health():
            ### 센서들의 상태 캘리브래이션 확인
            ### position 제어에 충분한지 확인
            if health.is_global_position_ok:
                print("Global position estimate ok")
                ### 제어에 충분하다면 출력
                break

        print("Fetching amsl altitude at home location....")
        async for terrain_info in drone.telemetry.home():
            absolute_altitude = terrain_info.absolute_altitude_m
            break

    async def drone_action(self):
        st = time.time()

        self.lock.acquire()
        print(f"Current Drone Mode : {self.data.control_mode}")
        self.lock.release()
        await asyncio.sleep(0.01)

        drone = System(mavsdk_server_address='localhost', port=50051)
        await drone.connect(system_address='serial:///dev/ttyTHS1:921600')

        print("Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print("Drone discovered")
                break

        print("Waiting for drone to have a global position estimate...")
        async for health in drone.telemetry.health():
            ### 센서들의 상태 캘리브래이션 확인
            ### position 제어에 충분한지 확인
            if health.is_global_position_ok:
                print("Global position estimate ok")
                ### 제어에 충분하다면 출력
                break

        print("Fetching amsl altitude at home location....")
        async for terrain_info in drone.telemetry.home():
            absolute_altitude = terrain_info.absolute_altitude_m
            print(f"absolute_altitude : {absolute_altitude}")
            break

        print(drone.telemetry)
        async for position in drone.telemetry.position():
            self.lock.acquire()

            self.data.lat_drone = position.latitude_deg
            self.data.lng_drone = position.longitude_deg
            lat_drone = self.data.lat_drone
            lng_drone = self.data.lng_drone

            print(f"current GPS : lat - {self.data.lat_drone} / lng - {self.data.lng_drone}")
            self.lock.release()
            print(f"current GPS : lat - {lat_drone} / lng - {lng_drone}")

        # print("-- Arming")
        # await drone.action.arm()
        # ### 이륙을 하지 않고 드론의 구동이 시작
        # ### 프로펠러가 돌기 시작함
        # flying_alt = 2.0
        # await drone.action.set_takeoff_altitude(flying_alt)
        # ### 이륙하면 도달한 드론의 고도를 절대고도+30으로 맞춤
        # await asyncio.sleep(2)
        # ### 위의 코드들을 실행하고 2초 정도 다른 명령을 주진 않음
        #
        # print("-- disarming --")
        # await drone.action.disarm()
        await asyncio.sleep(10)

        print('#D.D# drone action finished {}'.format(time.time() - st))

    def open_pixhawk_server(self):
        print("----OpenServer Thread Start")
        subprocess.run('sh ~/self-driving-drone/scripts/run_mavsdk_server.sh', shell=True)
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


