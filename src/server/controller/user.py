from flask import Blueprint, render_template
import os
from sys import path
path.append(os.path.dirname(os.path.abspath(__file__)))
from util.data import Data

blue_user = Blueprint("user", __name__, url_prefix="/user")
data = Data().instance()


@blue_user.route('/id')
def user_id():
    return 'id : Hozzi'

