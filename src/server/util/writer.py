import cv2
import os
from sys import path
import shutil
import datetime


class ImageWriter:
    def __init__(self):
        self.writer = cv2.VideoWriter()
        self.path = self.get_paths()
        self.zippath = self.path

    def get_paths(self):
        base_path = os.getcwd()
        return base_path

    def frame_to_video(self):
        pass

    def make_zip(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        shutil.make_archive(timestamp, 'zip', self.zippath)

    def run(self):
        self.frame_to_video()
        self.make_zip()