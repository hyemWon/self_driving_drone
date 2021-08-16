from flask import Blueprint, render_template
from src.server.util.data import DataCollector

blue_user = Blueprint("user", __name__, url_prefix="/user")


@blue_user.route('/id')
def user_id():
    return 'id : Hozzi'

