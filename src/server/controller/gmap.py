from flask import Blueprint, jsonify, request
import os
from sys import path
path.append(os.path.dirname(os.path.abspath(__file__)))
from util.data import Data

blue_gmap = Blueprint("gmap", __name__, url_prefix="/gmap")
data = Data().instance()


@blue_gmap.route("/dst/gps")
def dst_gps():
    # get destination gps point from request body

    return True
