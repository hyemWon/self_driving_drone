import firebase_admin
from firebase_admin import credentials, db

# import os
# from sys import path
# path.append(os.path.dirname(os.path.abspath(__file__)))
# from ..util.singleton import Singleton


class FireBase:
    def __init__(self):
        self.__cred = credentials.Certificate("keys/self-driving-drone-firebase-adminsdk-gbo40-14c39b1140.json")
        firebase_admin.initialize_app(self.__cred, {'databaseURL': 'https://self-driving-drone-default-rtdb.firebaseio.com/'})

        self.dir = db.reference()


if __name__ == '__main__':
    fb = FireBase()
    fb.dir.update(
        {
            'gps': {
                'current': [0.0, 0.0],
                'base': [0.0, 0.0],
                'src': [0.0, 0.0],
                'dst': [0.0, 0.0]
            }
        }
    )