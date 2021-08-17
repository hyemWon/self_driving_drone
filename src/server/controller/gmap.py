from flask import Blueprint, render_template
from ..util.data import Data

blue_gmap = Blueprint("gmap", __name__, url_prefix="/gmap")
data = Data().instance()


@blue_gmap.route("/drone/gps")
def drone_gps():
    return "--- [GPS] alt : {} / lng"


@blue_gmap.route("/drone/command")
def drone_command():
    return ""


@blue_gmap.route("/dst/gps")
def dst_gps():
    return ""
