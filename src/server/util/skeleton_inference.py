import argparse
import os
import platform
import sys
import time

import numpy as np
import torch
from tqdm import tqdm
import natsort

from detector.apis import get_detector
from trackers.tracker_api import Tracker
from trackers.tracker_cfg import cfg as tcfg
from trackers import track
from alphapose.models import builder
from alphapose.utils.config import update_config
from alphapose.utils.detector import DetectionLoader
from alphapose.utils.file_detector import FileDetectionLoader
from alphapose.utils.transforms import flip, flip_heatmap
from alphapose.utils.vis import getTime
from alphapose.utils.webcam_detector import WebCamDetectionLoader
from alphapose.utils.realsense_detector import RealSenseDetectionLoader
from alphapose.utils.writer import DataWriter

from .parser import ConfigParser
from .data import Data


class AlphaPoseDetector:
    def __init__(self):
        self.name = 'Alpha Pose Detector'
        self.data = Data().instance()
        self.path = os.path.join(os.getcwd(), 'util/alphapose_conf.yaml')

        # Argument Processing
        ConfigParser.load_config(self.path, 'yaml')
        self.args = ConfigParser.get_config()
        self.cfg = update_config(self.args.cfg)

        self.args.gpus = [int(i) for i in self.args.gpus.split(',')] if torch.cuda.device_count() >= 1 else [-1]
        self.args.device = torch.device("cuda:" + str(self.args.gpus[0]) if self.args.gpus[0] >= 0 else "cpu")
        self.args.detbatch = self.args.detbatch * len(self.args.gpus)
        self.args.posebatch = self.args.posebatch * len(self.args.gpus)
        self.args.tracking = self.args.pose_track or self.args.pose_flow or self.args.detector == 'tracker'

        # Load detection loader
        print('#SD# Loading detection')
        self.det_loader = RealSenseDetectionLoader(get_detector(self.args), self.cfg, self.args)

        # Load pose model
        self.pose_model = builder.build_sppe(self.cfg.MODEL, preset_cfg=self.cfg.DATA_PRESET)

        print('#SD# Loading pose model from %s...\n' % (self.args.checkpoint,))
        self.pose_model.load_state_dict(torch.load(self.args.checkpoint, map_location=self.args.device))
        self.pose_dataset = builder.retrieve_dataset(self.cfg.DATASET.TRAIN)
        if self.args.pose_track:
            self.tracker = Tracker(tcfg, self.args)
        if len(self.args.gpus) > 1:
            self.pose_model = torch.nn.DataParallel(self.pose_model, device_ids=self.args.gpus).to(self.args.device)
        else:
            self.pose_model.to(self.args.device)
        self.pose_model.eval()

    def print_finish_info(self):
        print('===========================> Finish Model Running.')
        if (self.args.save_img or self.args.save_video) and not self.args.vis_fast:
            print('===========================> Rendering remaining images in the queue...')
            print('===========================> If this step takes too long, you can enable the --vis_fast flag to use fast rendering (real-time).')

    def loop(self):
        n = 0
        while True:
            yield n
            n += 1

    def run(self, frame):
        if not self.args.sp:
            torch.multiprocessing.set_start_method('forkserver', force=True)
            torch.multiprocessing.set_sharing_strategy('file_system')

        # mode, input_source = self.check_input()
        mode, input_source = 'realsense', frame

        if not os.path.exists(self.args.outputpath):
            os.makedirs(self.args.outputpath)


        # if mode == 'webcam':
        #     det_loader = WebCamDetectionLoader(input_source, get_detector(self.args), self.cfg, self.args)
        #     det_worker = det_loader.start()
        # elif mode == 'detfile':
        #     det_loader = FileDetectionLoader(input_source, self.cfg, self.args)
        #     det_worker = det_loader.start()
        # elif mode == 'realsense':
        #     # --------- for realsense, input_source == frame
        #     det_loader = RealSenseDetectionLoader(input_source, get_detector(self.args), self.cfg, self.args)
        #     det_worker = det_loader.start()
        # else:
        #     det_loader = DetectionLoader(input_source, get_detector(self.args), self.cfg, self.args, batchSize=self.args.detbatch,
        #                                  mode=mode, queueSize=self.args.qsize)
        #     det_worker = det_loader.start()
        self.det_loader.load_frame(frame)
        det_worker = self.det_loader.start()

        runtime_profile = {
            'dt': [],
            'pt': [],
            'pn': []
        }

        # Init data writer
        queueSize = 2
        writer = DataWriter(self.cfg, self.args, save_video=False, queueSize=queueSize).start()

        if mode == 'webcam' or 'realsense':
            print('Starting webcam demo, press Ctrl + C to terminate...')
            sys.stdout.flush()
            im_names_desc = tqdm(self.loop())
        else:
            data_len = self.det_loader.length
            im_names_desc = tqdm(range(data_len), dynamic_ncols=True)

        batchSize = self.args.posebatch
        if self.args.flip:
            batchSize = int(batchSize / 2)
        try:
            for i in im_names_desc:
                start_time = getTime()
                with torch.no_grad():
                    (inps, orig_img, im_name, boxes, scores, ids, cropped_boxes) = self.det_loader.read()
                    if orig_img is None:
                        break
                    if boxes is None or boxes.nelement() == 0:
                        writer.save(None, None, None, None, None, orig_img, im_name)
                        continue
                    if self.args.profile:
                        ckpt_time, det_time = getTime(start_time)
                        runtime_profile['dt'].append(det_time)

                    # Pose Estimation
                    inps = inps.to(self.args.device)
                    datalen = inps.size(0)
                    leftover = 0
                    if (datalen) % batchSize:
                        leftover = 1
                    num_batches = datalen // batchSize + leftover
                    hm = []
                    for j in range(num_batches):
                        inps_j = inps[j * batchSize:min((j + 1) * batchSize, datalen)]
                        if self.args.flip:
                            inps_j = torch.cat((inps_j, flip(inps_j)))
                        hm_j = self.pose_model(inps_j)
                        if self.args.flip:
                            hm_j_flip = flip_heatmap(hm_j[int(len(hm_j) / 2):], self.pose_dataset.joint_pairs, shift=True)
                            hm_j = (hm_j[0:int(len(hm_j) / 2)] + hm_j_flip) / 2
                        hm.append(hm_j)
                    hm = torch.cat(hm)
                    if self.args.profile:
                        ckpt_time, pose_time = getTime(ckpt_time)
                        runtime_profile['pt'].append(pose_time)
                    if self.args.pose_track:
                        boxes, scores, ids, hm, cropped_boxes = track(self.tracker, self.args, orig_img, inps, boxes, hm,
                                                                      cropped_boxes, im_name, scores)
                    hm = hm.cpu()
                    writer.save(boxes, scores, ids, hm, cropped_boxes, orig_img, im_name)
                    if self.args.profile:
                        ckpt_time, post_time = getTime(ckpt_time)
                        runtime_profile['pn'].append(post_time)

                if self.args.profile:
                    # TQDM
                    im_names_desc.set_description(
                        'det time: {dt:.4f} | pose time: {pt:.4f} | post processing: {pn:.4f}'.format(
                            dt=np.mean(runtime_profile['dt']), pt=np.mean(runtime_profile['pt']),
                            pn=np.mean(runtime_profile['pn']))
                    )
            self.print_finish_info()
            while (writer.running()):
                time.sleep(1)
                print('===========================> Rendering remaining ' + str(
                    writer.count()) + ' images in the queue...')
            writer.stop()
            self.det_loader.stop()
        except Exception as e:
            print(repr(e))
            print('An error as above occurs when processing the images, please check it')
            pass
        except KeyboardInterrupt:
            self.print_finish_info()
            # Thread won't be killed when press Ctrl+C
            if self.args.sp:
                self.det_loader.terminate()
                while (writer.running()):
                    time.sleep(1)
                    print('===========================> Rendering remaining ' + str(
                        writer.count()) + ' images in the queue...')
                writer.stop()
            else:
                # subprocesses are killed, manually clear queues

                self.det_loader.terminate()
                writer.terminate()
                writer.clear_queues()
                self.det_loader.clear_queues()
