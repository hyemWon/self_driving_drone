import cv2
import os
from sys import path
import shutil
import datetime


class ImageWriter:
    def __init__(self, _name, _fps, _size):
        self.name = _name
        self.fps = _fps
        self.size = _size
        self.fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        self.base_path = os.getcwd()
        self.timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        self.video_base_path = "/home/piai/PycharmProjects/self_driving_drone/video"
        # self.zip_path =
        self.video_output_path = "/home/piai/PycharmProjects/self_driving_drone/video/{}".format(self.timestamp)
        self.makedir()

        self.video_writer = cv2.VideoWriter(os.path.join(self.video_output_path, f"{self.name}.avi"),
                                            self.fourcc, self.fps, self.size)

    def get_paths(self):
        base_path = os.getcwd()
        return base_path

    def video_write(self, frame):
        self.video_writer.write(frame)

    def makedir(self):
        if not os.path.isdir(self.video_base_path):
            os.mkdir(self.video_base_path)
        if not os.path.isdir(self.video_output_path):
            os.mkdir(self.video_output_path)

    @classmethod
    def image_write(cls, _fname, _frame):
        cv2.imwrite(_fname, _frame)
