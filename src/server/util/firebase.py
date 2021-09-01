import firebase_admin
from firebase_admin import credentials, db
import os

from .singleton import Singleton


class FireBase(Singleton):
    def __init__(self):
        self.cred_path = os.path.join(os.getcwd(), "db/keys/self-driving-drone-firebase-adminsdk-gbo40-14c39b1140.json")
        self.__cred = credentials.Certificate(self.cred_path)
        firebase_admin.initialize_app(self.__cred, {'databaseURL': 'https://self-driving-drone-default-rtdb.firebaseio.com/'})

        self.dir = db.reference()

# if __name__ == '__main__':
#     fb = FireBase()
#     print(fb.cred_path)