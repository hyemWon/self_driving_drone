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

        # drone instance and information
        self.drone = None
        self.absolute_altitude = None

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
        time.sleep(0.5)
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
                lat_drone = self.data.gps_point['current'][0]
                lng_drone = self.data.gps_point['current'][1]
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
                self.data.gps_point['end'][0] = float(lat_dst)
                self.data.gps_point['end'][1] = float(lng_dst)
                if control_mode != -1 and self.data.drone_is_doing_action:
                    self.data.control_mode = int(control_mode)
                self.lock.release()

                time.sleep(0.05)
                print('#D.S# socket job finished {}'.format(self.host_name, time.time() - st))
                print(lat_drone, lng_drone, lat_dst, lng_dst)
            except Exception as e:
                self.isRunSocket = False
                print(e)
                print(f"-------- Close {self.host_name}")

    def thread_drone(self):
        # Step 1) Set async loop and check drone connection
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        drone = loop.run_until_complete(self.check_drone_state())
        time.sleep(0.01)

        if not drone:
            self.isRunDrone = False
            loop.close()
            print("### --- Please Check drone state")

        while self.isRunDrone:
            try:
                # Step 2)Get drone mode from data
                self.lock.acquire()
                flight_mode = self.data.control_mode
                print(f"Current Drone Mode : {flight_mode}")
                self.data.drone_is_doing_action = True
                self.lock.release()

                # Step 3)Start action by drone mode
                if flight_mode == 1:
                    loop.run_until_complete(self.action_goto_gps_point('dst'))  # action go to gps point
                elif flight_mode == 2:
                    loop.run_until_complete(self.action_just_arming_and_disarming())  # action just arming
                elif flight_mode == 3:
                    loop.run_until_complete(self.action_takeoff_and_landing())  # action landing
                elif flight_mode == 4:
                    loop.run_until_complete(self.action_by_keyboard())  # action by using keyboard
                # elif flight_mode == 5:
                #     loop.run_until_complete()
                else:
                    print("Command 0 State")
                    time.sleep(0.2)  # delay 0.2s

                # Step 4) Set drone mode 0(default) or next mode in async function

            except Exception as e:
                self.isRunDrone = False

                loop.close()
                print(e)
                print(f"-------- Close {self.host_name}")

    def thread_drone_shutdown(self):
        self.lock.acquire()
        self.data.control_mode = 0
        self.lock.release()
        # shutdown
        self.isRunDrone = False

    # mode == 1 : go to gps point
    async def action_goto_gps_point(self, dst_name):
        st = time.time()
        err = 0.00005
        await asyncio.sleep(0.01)

        # get destination point
        self.lock.acquire()
        lat_dst = self.data.gps_point[dst_name][0]
        lng_dst = self.data.gps_point[dst_name][1]
        self.lock.release()

        print("#-- Arming")
        await self.drone.action.arm()
        await self.drone.set_maximum_speed(20)
        flying_alt = self.absolute_altitude + 10.0
        await self.drone.action.set_takeoff_altitude(flying_alt)
        await asyncio.sleep(1)

        print("#-- Taking off")
        await self.drone.action.takeoff()
        await asyncio.sleep(10)

        # moving to gps position
        print("# -- Going to GPS point")
        await self.drone.action.goto_location(lat_dst, lng_dst, flying_alt, float('nan'))
        async for position in self.drone.telemetry.position():
            lat_drone = position.latitude_deg
            lng_drone = position.longitude_deg

            # save current gps_points
            self.lock.acquire()
            self.data.gps_point['current'][0] = lat_drone
            self.data.gps_point['current'][1] = lng_drone
            self.lock.release()

            # if
            if (lat_dst - err <= lat_drone <= lat_dst - err) and (
                    lng_dst - err <= lng_drone <= lng_dst + err):
                await self.drone.action.goto_location(lat_dst, lng_dst, flying_alt, 0)
                break

        print("# -- Arrived and waiting --")
        await asyncio.sleep(4)

        print("# -- Landing --")
        await self.drone.action.land()
        await asyncio.sleep(10)

        print("# -- Disarming --")
        await self.drone.action.disarm()
        await asyncio.sleep(5)

        # next mode set by 0
        self.lock.acquire()
        self.data.control_mode = 0
        self.data.drone_is_doing_action = False
        self.lock.release()
        print('#D.D# drone action finished {}'.format(time.time() - st))

    # mode == 2 : arming and disarming
    async def action_just_arming_and_disarming(self):
        await asyncio.sleep(0.01)

        print("-- Arming")
        await self.drone.action.arm()
        await asyncio.sleep(2)

        print("-- disarming --")
        await self.drone.action.disarm()
        await asyncio.sleep(5)

        # next mode set by 0
        self.lock.acquire()
        self.data.control_mode = 0
        self.data.drone_is_doing_action = False
        self.lock.release()

    # mode == 3 : take off and landing
    async def action_takeoff_and_landing(self):
        await asyncio.sleep(0.01)
        print("-- Arming --")
        await self.drone.action.arm()
        await asyncio.sleep(5)

        print("-- Set take off altitude --")
        flying_alt = self.absolute_altitude + 5.0       # flying_alt = 2.0
        await self.drone.action.set_takeoff_altitude(flying_alt)
        await asyncio.sleep(2)

        print("-- Taking off --")
        await self.drone.action.takeoff()
        await asyncio.sleep(10)

        print("-- Landing --")
        await self.drone.action.land()
        await asyncio.sleep(15)

        print("-- Disarming --")
        await self.drone.action.disarm()
        await asyncio.sleep(5)

        # next mode set by 0
        self.lock.acquire()
        self.data.control_mode = 0
        self.data.drone_is_doing_action = False
        self.lock.release()

    # mode == 4 : Keyboard Control mode
    async def action_by_keyboard(self):
        # print("# -- [Roll] : e,d / [Pitch] : s,f \n# -- [Yaw] : j,l / [Throttle] : i,k\n")
        # direction, second = input("### Keyboard Input (Direction, second): ").split(sep=' ')
        # second = int(second)
        #
        # print(direction, second)
        print("# -- Arming")
        await self.drone.action.arm()
        await self.drone.set_maximum_speed(20)
        flying_alt = self.absolute_altitude + 10.0
        await self.drone.action.set_takeoff_altitude(flying_alt)
        await asyncio.sleep(1)

        print("# -- Taking off")
        await self.drone.action.takeoff()
        await asyncio.sleep(10)

        print("# -- Setting initial setpoint")
        await self.drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

        print("# -- Starting offboard mode")
        try:
            await self.drone.offboard.start()
        except OffboardError as error:
            print(f"Starting offboard mode failed with error code: {error._result.result}")
            print("# -- Disarming")
            await self.drone.action.land()
            await self.drone.action.disarm()
            return

        ch, prev_ch = '', ''
        # VelocityBodyYawspeed(front(+)/back(-), right(+)/left(-), down(+)/up(-) , clockwise(+)/counterclockwise(-))
        while ch != 'q':
            # action : [forward/backward] : e,d            / [left/right] : s,f
            #          [clockwise/counterclockwise] : j,l  / [up/donw] : i,k
            ch = input("### ----- Input Char : ").lower()
            if ch != prev_ch:
                await self.drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
                await asyncio.sleep(1)

                if ch == 'e':
                    await self.go_forward()
                elif ch == 'd':
                    await self.go_backward()
                elif ch == 'f':
                    await self.go_right()
                elif ch == 's':
                    await self.go_left()
                elif ch == 'i':
                    await self.go_up()
                elif ch == 'k':
                    await self.go_down()
                elif ch == 'j':
                    await self.turn_clockwise()
                elif ch == 'l':
                    await self.turn_counterclockwise()
                elif ch == 'h':
                    await self.hold_position()
        await asyncio.sleep(0.2)

        await self.drone.action.land()
        await asyncio.sleep(10)
        await self.drone.action.disarm()
        await asyncio.sleep(5)

        # next mode set by 0
        self.lock.acquire()
        self.data.control_mode = 0
        self.data.drone_is_doing_action = False
        self.lock.release()

    # mode == 5 : Person Following mode
    async def action_detection_person_and_following(self, drone):
        await asyncio.sleep(0.01)

        # while entering command
        ## 1) get detection information from server (bounding box,

        ## 2) determine drone how to move

        # 3) end

        self.lock.acquire()
        self.data.control_mode = 0
        self.data.drone_is_doing_action = False
        self.lock.release()

    # mode == 6 : Person recognize mode
    async def recognize_person(self):
        await asyncio.sleep(0.01)
        pass
        # 1) get information from data

        self.lock.acquire()
        self.data.control_mode = 0
        self.data.drone_is_doing_action = False
        self.lock.release()

    async def check_drone_state(self):
        print("#-- Checking Drone State...")
        await asyncio.sleep(1)

        drone = System(mavsdk_server_address='localhost', port=50051)
        await drone.connect(system_address='serial:///dev/ttyTHS1:921600')

        print("#-- Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print(f"#--- Drone discovered")
                break

        print("#-- Waiting for drone to have a global position estimate...")
        async for health in drone.telemetry.health():
            if health.is_global_position_ok:
                print("#--- Global position estimate ok")
                break

        print("# Fetching amsl altitude at home location....")
        async for terrain_info in drone.telemetry.home():
            self.absolute_altitude = terrain_info.absolute_altitude_m
            break

        return drone

    def open_pixhawk_server(self):
        print("----OpenServer Thread Start")
        print("----Mavsdk Server Start!----")
        print("#############################################################################")
        subprocess.run('sh ~/self_driving_drone/scripts/run_mavsdk_server.sh', shell=True)
        print("----Mavsdk Server End!----")

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

    # -------------- Keyboard Commands
    async def go_forward(self, sec=1):
        await self.drone.offborad.set_velocity_body(
            VelocityBodyYawspeed(1.0, 0.0, 0.0, 0.0))
        await asyncio.sleep(sec)

    async def go_backward(self, sec=1):
        await self.drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(-1.0, 0.0, 0.0, 0.0))
        await asyncio.sleep(sec)

    async def go_right(self, sec=1):
        await self.drone.offborad.set_velocity_body(
            VelocityBodyYawspeed(0.0, 1.0, 0.0, 0.0))
        await asyncio.sleep(sec)

    async def go_left(self, sec=1):
        await self.drone.offborad.set_velocity_body(
            VelocityBodyYawspeed(0.0, -1.0, 0.0, 0.0))
        await asyncio.sleep(sec)

    async def go_down(self, sec=1):
        await self.drone.offborad.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, -1.0, 0.0))
        await asyncio.sleep(sec)

    async def go_up(self, sec=1):
        await self.drone.offborad.set_velocity_body(
            VelocityBodyYawspeed(0.0, -1.0, 0.0, 0.0))
        await asyncio.sleep(sec)

    async def turn_clockwise(self, sec=4):
        await self.drone.offborad.set_velocity_body(
            VelocityBodyYawspeed(0.0, -1.0, 0.0, 0.0)
        )
        await asyncio.sleep(sec)

    async def turn_counterclockwise(self, sec=4):
        await self.drone.offborad.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, -60.0)
        )
        await asyncio.sleep(sec)

    async def hold_position(self, sec=2):
        await self.drone.offborad.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
        )
        await asyncio.sleep(sec)

