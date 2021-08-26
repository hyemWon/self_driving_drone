from flask import Blueprint, jsonify, request
import os
from sys import path
path.append(os.path.dirname(os.path.abspath(__file__)))
from util.data import Data

blue_drone = Blueprint("drone", __name__, url_prefix="/drone")
data = Data().instance()


@blue_drone.route("/gps", methods=['GET'])
def gps():
    data.lock.acquire()
    lat = data.gps_point['current'][0]
    lng = data.gps_point['current'][1]
    data.lock.release()

    # f"--- [GPS] lat : {lat} / lng {lng}"
    return jsonify({
        'current': {
            'lat': lat,
            'lng': lng
        }
    })


@blue_drone.route("/command")
def command():
    cmd = request.args.get('command', 0)   # default mode == -1

    data.lock.acquire()
    data.control_mode = int(cmd)
    data.lock.release()

    return jsonify({
        'command': cmd
    })
