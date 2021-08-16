from flask import Blueprint, render_template
from src.server.util.data import DataCollector

blue_gmap = Blueprint("gmap", __name__, url_prefix="/gmap")
# data_collector = DataCollector()

@blue_gmap.route("/drone/gps")
def drone_gps():
    return "--- [GPS] alt : {} / lng"


@blue_gmap.route("/drone/")
def gps_app_to_drone():
    return ""