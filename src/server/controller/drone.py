from flask import Blueprint, jsonify, request
import os
from sys import path
path.append(os.path.dirname(os.path.abspath(__file__)))
from util.data import Data

blue_drone = Blueprint("drone", __name__, url_prefix="/drone")
data = Data().instance()


@blue_drone.route("/gps")
def gps():
    data.lock.acquire()
    lat = data.lat_drone
    lng = data.lng_drone
    data.lock.release()

    # f"--- [GPS] lat : {lat} / lng {lng}"
    return jsonify({
        'lat': lat,
        'lng': lng
    })


@blue_drone.route("/command")
def command():
    cmd = request.args.get('command', 0)   # default mode == -1

    data.lock.acquire()
    data.control_mode = cmd
    data.lock.release()

    return jsonify({
        'command': cmd
    })
