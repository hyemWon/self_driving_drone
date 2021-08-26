# import argparse
# import os
# import platform
# import sys
# import time
#
# import numpy as np
# import torch
# from tqdm import tqdm
# import natsort
#
# from detector.apis import get_detector
# from trackers.tracker_api import Tracker
# from trackers.tracker_cfg import cfg as tcfg
# from trackers import track
# from alphapose.models import builder
# from alphapose.utils.config import update_config
# from alphapose.utils.detector import DetectionLoader
# from alphapose.utils.transforms import flip, flip_heatmap
# from alphapose.utils.vis import getTime
# from alphapose.utils.webcam_detector import WebCamDetectionLoader
# from alphapose.utils.writer import DataWriter
#
#
# class AlphaPoseDetector:
#     def __init__(self):
#         self.name = 'alpha pose'
#         self.conf = None
#         self.args = None
#         self.path = ''
#
#     # def set_conf(self):
#     #     with open(self.path, 'w') as f:
#     #         yaml.dump(self.conf, f)
#     #
#     # def load_conf(self):
#     #     with open(self.path) as f:
#     #         self.conf = yaml.load(f)
#
#     def init_args(self):
#         self.args = parser.parse_args()     # parser
#         # pprint.pprint(self.args)
#         cfg = update_config(self.args.cfg)
#
#         if platform.system() == 'Windows':
#             self.args.sp = True
#
#         self.args.gpus = [int(i) for i in self.args.gpus.split(',')] if torch.cuda.device_count() >= 1 else [-1]
#         self.args.device = torch.device("cuda:" + str(self.args.gpus[0]) if self.args.gpus[0] >= 0 else "cpu")
#         self.args.detbatch = self.args.detbatch * len(self.args.gpus)
#         self.args.posebatch = self.args.posebatch * len(self.args.gpus)
#         self.args.tracking = self.args.pose_track or self.args.pose_flow or self.args.detector == 'tracker'
#
#         if not self.args.sp:
#             torch.multiprocessing.set_start_method('forkserver', force=True)
#             torch.multiprocessing.set_sharing_strategy('file_system')
#
#     def check_input(self):
#         # for wecam
#         if self.args.webcam != -1:
#             self.args.detbatch = 1
#             return 'webcam', int(self.args.webcam)
#
#         # for video
#         if len(self.args.video):
#             if os.path.isfile(self.args.video):
#                 videofile = self.args.video
#                 return 'video', videofile
#             else:
#                 raise IOError('Error: --video must refer to a video file, not directory.')
#
#         # for detection results
#         if len(self.args.detfile):
#             if os.path.isfile(self.args.detfile):
#                 detfile = self.args.detfile
#                 return 'detfile', detfile
#             else:
#                 raise IOError('Error: --detfile must refer to a detection json file, not directory.')
#
#         # for images
#         if len(self.args.inputpath) or len(self.args.inputlist) or len(self.args.inputimg):
#             inputpath = self.args.inputpath
#             inputlist = self.args.inputlist
#             inputimg = self.args.inputimg
#
#             if len(inputlist):
#                 im_names = open(inputlist, 'r').readlines()
#             elif len(inputpath) and inputpath != '/':
#                 for root, dirs, files in os.walk(inputpath):
#                     im_names = files
#                 im_names = natsort.natsorted(im_names)
#             elif len(inputimg):
#                 self.args.inputpath = os.path.split(inputimg)[0]
#                 im_names = [os.path.split(inputimg)[1]]
#
#             return 'image', im_names
#
#         else:
#             raise NotImplementedError
#
#     def print_finish_info(self):
#         print('===========================> Finish Model Running.')
#         if (self.args.save_img or self.args.save_video) and not self.args.vis_fast:
#             print('===========================> Rendering remaining images in the queue...')
#             print(
#                 '===========================> If this step takes too long, you can enable the --vis_fast flag to use fast rendering (real-time).')
#
#     def loop(self):
#         n = 0
#         while True:
#             yield n
#             n += 1
