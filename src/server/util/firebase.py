import firebase_admin
from firebase_admin import credentials, db
import os

from .singleton import Singleton


class FireBase(Singleton):
    def __init__(self):
        self.cred_path = os.path.join(os.getcwd(), "user_key_file.json")
        self.__cred = credentials.Certificate(self.cred_path)
        firebase_admin.initialize_app(self.__cred, {'databaseURL': 'user_firebase_url_path'})

        self.dir = db.reference()
