#!/usr/bin/env python3
import asyncio
import threading
import time
import os
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)


object_lat = 36.01305 ### 도착지 위도
object_lon = 129.319452 ### 도착지 경도

def openServer() :
    print("----OpenServer Thread Start")
    sudoPassword = '1'
    print("1")
    command = "./mavsdk_server -p 50051 serial:///dev/ttyTHS1:921600"
    print("2")
    os.chdir("/home/b/MAVSDK-Python/mavsdk/bin")
    print("3")
    os.system('echo %s|sudo -S %s' %(sudoPassword,command))
    print("----Server Start!----")
    print("#############################################################################")


async def run():
    print("#############################################################################")
    print("StartDrone!!!!!!!!!!!!!")
    flag = False
    if flag == False:
        s = threading.Thread(target=openServer)
        s.start()
        flag = True
        time.sleep(3)

    drone = System(mavsdk_server_address='localhost', port=50051)
    await drone.connect(system_address="serial:///dev/ttyTHS1:921600")


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
    flying_alt = absolute_altitude + 1.0
    print("고도는:{}".format(flying_alt))

    print("-- Arming")
    await drone.action.arm()
    ### 이륙을 하지 않고 드론의 구동이 시작
    ### 프로펠러가 돌기 시작함
    await drone.action.set_takeoff_altitude(flying_alt)
    ### 이륙하면 도달한 드론의 고도를 절대고도+30으로 맞춤
    await asyncio.sleep(6)
    ### 위의 코드들을 실행하고 2초 정도 다른 명령을 주진 않음

    print("-- Taking off")
    await drone.action.takeoff()
    ### 드론 이륙
    await asyncio.sleep(10)
    ### 드론이 이륙하기 시작한 10초 동안 다음 코드를 실행하지 않음
    ### 만약 10초 동안 드론이 flying_alt 고도까지 도달하지 못하면
    ### 도달할 때까지 goto_location 명령이 실행돼도 위도 경도에 대한 변동은 크지 않고 고도에 대한 변동만 일어남


    await drone.action.land()
    print("-- landing start! --")
    await asyncio.sleep(15)

    print("-- disarming --")
    await drone.action.disarm()
    await asyncio.sleep(10)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    # asyncio.ensure_future(run())
    # asyncio.get_event_loop().run_forever()
