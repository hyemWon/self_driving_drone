# Original Code from
# https://github.com/LaboratoireMecaniqueLille/Seek-thermal-Python

import usb.core
import usb.util
import numpy as np
import cv2
from time import time


class SeekPro:
    """
    Seekpro class:
      Can read images from the Seek Thermal pro camera
      Can apply a calibration from the integrated black body
      Can locate and remove dead pixels
    This class only works with the PRO version !
    """
    def __init__(self):
        # seek comapct pro usb info : idVender = 0x289d, idProduct = 0x0011
        self.codes = {
            # Address enum
            'READ_CHIP_ID': 54,  # 0x36
            'START_GET_IMAGE_TRANSFER': 83,     # 0x53

            'GET_OPERATION_MODE': 61,       # 0x3D
            'GET_IMAGE_PROCESSING_MODE': 63,    # 0x3F
            'GET_FIRMWARE_INFO': 78,        # 0x4E
            'GET_FACTORY_SETTINGS': 88,     # 0x58

            'SET_OPERATION_MODE': 60,       # 0x3C
            'SET_IMAGE_PROCESSING_MODE': 62,    # 0x3E
            'SET_FIRMWARE_INFO_FEATURES': 85,   # 0x55
            'SET_FACTORY_SETTINGS_FEATURES': 86  # 0x56
        }

        self.width = 320
        self.height = 240
        self.raw_width = 342
        self.raw_height = 260
        self.dev = usb.core.find(idVendor=0x289d, idProduct=0x0011)

        if not self.dev:
            raise IOError('Device not found')

        self.dev.set_configuration()
        self.calib = None
        for i in range(5):
            # Sometimes, the first frame does not have id 4 as expected...
            # Let's retry a few times
            if i == 4:
                # If it does not work, let's forget about dead pixels!
                print("Could not get the dead pixels frame!")
                self.dead_pixels = []
                break
            self.init()
            status, ret = self.grab()
            if status == 4:
                self.dead_pixels = self.get_dead_pix_list(ret)
                break


    def get_dead_pix_list(self, data):
        """
        Get the dead pixels image and store all the coordinates
        of the pixels to be corrected
        """
        img = self.crop(np.frombuffer(data, dtype=np.uint16).reshape(
            self.raw_height, self.raw_width))
        return list(zip(*np.where(img < 100)))

    def correct_dead_pix(self, img):
        """For each dead pix, take the median of the surrounding pixels"""
        for i, j in self.dead_pixels:
            img[i, j] = np.median(img[max(0, i-1): i+2, max(0, j-1):j+2])
        return img

    def crop(self, raw_img):
        """Get the actual image from the raw image"""
        return raw_img[4:4+self.height, 1:1+self.width]

    def send_msg(self, bRequest, data_or_wLength, wValue=0,
                 wIndex=0, bmRequestType=0x41, timeout=None):
        """
        Wrapper to call ctrl_transfer with default args to enhance readability
        """
        assert (self.dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex,
                                       data_or_wLength, timeout) == len(data_or_wLength))

    def receive_msg(self, bRequest, data, wValue=0, wIndex=0, bmRequestType=0xC1,
                    timeout=None):
        """
        Wrapper to call ctrl_transfer with default args to enhance readability
        """
        return self.dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex,
                                      data, timeout)

    def deinit(self):
        """
        Is it useful ?
        """
        for i in range(3):
            self.send_msg(0x3C, b'\x00\x00')

    def init(self):
        """
        Sends all the necessary data to init the camera
        """
        self.send_msg(self.codes['SET_OPERATION_MODE'], b'\x00\x00')
        # r = receive_msg(GET_FIRMWARE_INFO, 4)
        # print(r)
        # r = receive_msg(READ_CHIP_ID, 12)
        # print(r)
        self.send_msg(self.codes['SET_FACTORY_SETTINGS_FEATURES'], b'\x06\x00\x08\x00\x00\x00')
        # r = receive_msg(GET_FACTORY_SETTINGS, 12)
        # print(r)
        self.send_msg(self.codes['SET_FIRMWARE_INFO_FEATURES'], b'\x17\x00')
        # r = receive_msg(GET_FIRMWARE_INFO, 64)
        # print(r)
        self.send_msg(self.codes['SET_FACTORY_SETTINGS_FEATURES'], b"\x01\x00\x00\x06\x00\x00")
        # r = receive_msg(GET_FACTORY_SETTINGS,2)
        # print(r)
        for i in range(10):
            for j in range(0, 256, 32):
                self.send_msg(
                    self.codes['SET_FACTORY_SETTINGS_FEATURES'], b"\x20\x00"+bytes([j, i])+b"\x00\x00")
                # r = receive_msg(GET_FACTORY_SETTINGS,64)
                # print(r)
        self.send_msg(self.codes['SET_FIRMWARE_INFO_FEATURES'], b"\x15\x00")
        # r = receive_msg(GET_FIRMWARE_INFO,64)
        # print(r)
        self.send_msg(self.codes['SET_IMAGE_PROCESSING_MODE'], b"\x08\x00")
        # r = receive_msg(GET_IMAGE_PROCESSING_MODE,2)
        # print(r)
        self.send_msg(self.codes['SET_OPERATION_MODE'], b"\x01\x00")
        # r = receive_msg(GET_OPERATION_MODE,2)
        # print(r)

    def grab(self):
        """
        Asks the device for an image and reads it
        """
        # Send read frame request
        self.send_msg(self.codes['START_GET_IMAGE_TRANSFER'], b'\x58\x5b\x01\x00')
        toread = 2*self.raw_width*self.raw_height
        ret = self.dev.read(0x81, 13680, 1000)
        remaining = toread-len(ret)
        # 512 instead of 0, to avoid crashes when there is an unexpected offset
        # It often happens on the first frame
        while remaining > 512:
            # print(remaining," remaining")
            ret += self.dev.read(0x81, 13680, 1000)
            remaining = toread-len(ret)
        status = ret[4]
        if len(ret) == self.raw_width*self.raw_height*2:
            return status, np.frombuffer(ret, dtype=np.uint16).reshape(
                self.raw_height, self.raw_width)
        else:
            return status, None

    def get_image(self):
        """
        Method to get an actual IR image
        """
        while True:
            status, img = self.grab()
            # print("Status=",status)
            if status == 1:     # Calibration frame
                self.calib = self.crop(img)-1600
            elif status == 3:   # Normal frame
                if self.calib is not None:
                    return self.correct_dead_pix(self.crop(img)-self.calib)

    def rescale(self, img):
        """
        To adapt the range of values to the actual min and max and cast it into
        an 8 bits image
        """
        if img is None:
            return np.array([0])
        mini = img.min()    # min pixel data
        maxi = img.max()    # max pixel data

        return (np.clip(img-mini, 0, maxi-mini)/(maxi-mini)*255.).astype(np.uint8)


if __name__ == '__main__':
    cam = SeekPro()

    cv2.namedWindow("Seek", cv2.WINDOW_NORMAL)

    t0 = time()
    while True:
        t = time()
        print("fps:", 1/(t-t0))
        t0 = time()
        r = cam.get_image()
        cv2.imshow("Seek", cam.rescale(r))
        cv2.waitKey(1)
