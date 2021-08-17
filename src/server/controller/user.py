from flask import Blueprint, render_template
from ..util.data import Data

blue_user = Blueprint("user", __name__, url_prefix="/user")
data = Data().instance()


@blue_user.route('/id')
def user_id():
    return 'id : Hozzi'

