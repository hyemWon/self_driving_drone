import asyncio
import threading
import numpy as np

from util.data import Data, FrameQueue
from util.writer import ImageWriter
# from util.skeleton_inference import AlphaPoseDetector
from util.person_tracking import PersonTracker
import time


class ImageProcessor:
    def __init__(self):
        self.host_name = 'Image Processor'
        self.frame_queue = FrameQueue().instance()
        # self.writer = ImageWriter()
        # -- Detectors
        self.person_detector = PersonTracker()
        self.alpha_pose_detector = None     # AlphaPoseDetector()
        self.obstacle_detector = None       # ObstacleDetector()
        self.isRun = False

    def run(self):
        t = threading.Thread(target=self.thread)
        t.daemon = True
        self.isRun = True
        t.start()

    def thread(self):
        print(f"-------- {self.host_name} start")
        # start image processing
        while True:
            try:
                # st = time.time()
                frame = self.frame_queue.pop()

                if frame is not None:
                    asyncio.run(self.start_processing(frame))
                # print(f"#IP# process finished {time.time()-st}")
                time.sleep(0.02)
            except Exception as e:
                print(e)
                self.isRun = False
                # self.writer.run()
                print("-------- Close {}".format(self.host_name))

    async def start_processing(self, frame):
        print("#IM# Start Processing")
        result = await asyncio.gather(self.person_detection(frame.copy()),
                                      self.skeleton_detection(frame.copy()),
                                      self.obstacle_detection(frame.copy()))

        print(result)
        # await asyncio.gather(self.person_processing(results[0]),
        #                      self.skeleton_processing(results[1]),
        #                      self.obstacle_processing(results[2]))

    async def person_detection(self, frame):
        try:
            return self.person_detector.run(frame)
        except Exception as e:
            print(f'# person detection error\n## {e}')
            return None

    async def skeleton_detection(self, frame):
        # try:
        #     return self.alpha_pose_detector.run(frame)
        # except Exception as e:
        #     print(f'# skeleton detection error\n## {e}')
        #     return None
        return []

    async def obstacle_detection(self, frame):
        return []

    async def person_processing(self, person):
        return [0]

    async def skeleton_processing(self, skeleton):
        return [1]

    async def obstacle_processing(self, obstacle):
        return [2]
