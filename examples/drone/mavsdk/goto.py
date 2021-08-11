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
    flying_alt = 5.0
    # flying_alt = absolute_altitude + 6.0
    print("고도는:{}".format(flying_alt))

    print("-- Arming")
    await drone.action.arm()
    ### 이륙을 하지 않고 드론의 구동이 시작
    ### 프로펠러가 돌기 시작함
    await drone.action.set_takeoff_altitude(flying_alt)
    await asyncio.sleep(6)
    ### 위의 코드들을 실행하고 2초 정도 다른 명령을 주진 않음

    print("-- Taking off")
    await drone.action.takeoff()
    ### 드론 이륙
    await asyncio.sleep(10)
    ### 드론이 이륙하기 시작한 10초 동안 다음 코드를 실행하지 않음
    ### 만약 10초 동안 드론이 flying_alt 고도까지 도달하지 못하면
    ### 도달할 때까지 goto_location 명령이 실행돼도 위도 경도에 대한 변동은 크지 않고 고도에 대한 변동만 일어남

    # GPS 위도/경도 수신하면, 목적지로 이동하는 코드
    print(drone.telemetry)
    await drone.action.goto_location(object_lat, object_lon, float('nan'), float('nan'))
    ### object_lat = 36.012903  ### 도착지 위도
    ### object_lon = 129.318985  ### 도착지 경도
    ### goto_location(위도, 경도, 고도, yaw)
    ### yaw는 드론의 머리가 향하는 방향
    ### float('nan')은 그냥 우리가 설정해주지 않고 알아서 맞춰지는 느낌인 듯
    index = 0
    async for position in drone.telemetry.position():
        ### telemetry.position(): 드론의 gps를 받음
        ### position()이 실시간으로 갱신될 건데 갱신되는 position을 계속 출력하려 함
        ### index가 0일 때 드론의 gps값 드론이 이동하기 시작한 때의 gps값
        ### 택배 배송 후 돌아올 gps값을 미리 설정하려 함
        if index == 0:
            home_lat = position.latitude_deg
            home_lon = position.longitude_deg
            ### home_lat은 돌아올 위도값
        index = index + 1
        lat = position.latitude_deg
        ### 현재 위도값
        lon = position.longitude_deg
        ### 현재 경도값

        print(f"latitude : {lat} / longitude : {lon}")
        ### 위도, 경도 출력

        #############################################################

        ### lat, lon을 워크스테이션으로 보내주면 워크스테이션에서 실시간으로 드론의 gps값 확인 가능할 거 같다

        #############################################################


        if (object_lat - 0.00005 <= lat <= object_lat + 0.00005) and (
                ### gps만으로 위치를 판단하면 정확하지 않으므로 드론의 gps값이 어느정도 목표 gps값과 비슷해지면 도착했다 판단
                ### if( 위도가 목표위도-0.00005와 목표위도+0.00005 사이 )
                object_lon - 0.00005 <= lon <= object_lon + 0.00005):


            await drone.action.goto_location(object_lat, object_lon, float('nan'), 0)
            ### 목적지에 도착하면, yaw를 0도(북쪽)으로 변경
            ### 이 await 코드는 해당위치를 기준으로 오른쪽, 왼쪽 등 방향으로 이동할 때 기준 방향이 필요해서 넣은 것으로 추측
            ### 우리는 필수가 아닌 거 같다
            print("도착!!!!")
            print(position)
            break
            ### 도착하면 if문에서 break



    #############################################################

    ### 여기에 YOLO 조건 맞으면 착륙하는 코드 있으면 될 거같다

    #############################################################

    await asyncio.sleep(5)
    ### 도착하면 5초 쉬고




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
