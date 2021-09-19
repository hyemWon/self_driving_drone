# TODO: processor turned into multi-process
# import asyncio
# import threading
# import multiprocessing
#
# import cv2
# import numpy as np
#
# from util.data import Data, FrameQueue
# # from util.actionai_pose_inference import ActionAIPoseDetector
# from util.person_tracking import PersonTracker
# from util.writer import ImageWriter
# import time
#
#
# class ImageProcessor:
#     def __init__(self):
#         self.host_name = 'Multi-processing Image Processor'
#         self.frame_queue = FrameQueue().instance()
#         # -- Detectors
#         self.person_detector = PersonTracker()
#         # self.pose_detector = ActionAIPoseDetector()
#         # self.action_ai_pose_detector = PoseDetector()
#         self.obstacle_detector = None       # ObstacleDetector()
#
#         self.origin_video_writer = ImageWriter('original', 10.0, (960, 540))
#         self.result_video_writer = ImageWriter('result', 10.0, (960, 540))
#         self.isRun = False
#         self.cnt = 0
#
#     def run(self):
#         p_person_detection = multiprocessing.Process(target=)
#         p_pose_detection = multiprocessing.Process(target=)
#         p_obstacle_detection = multiprocessing.Process(target=)
#
#         mp.join()
#
#     def thread(self):
#         print(f"-------- {self.host_name} start")
#         # start image processing
#         while self.isRun:
#             try:
#                 st = time.time()
#                 frame = self.frame_queue.pop()
#
#                 if frame is not None:
#                     asyncio.run(self.start_processing(frame.copy()))
#                     cv2.imwrite("imgs/rgb/frame_{}.jpg".format(self.cnt), frame)    # write frame image
#                     self.origin_video_writer.video_write(frame)                     # write video
#
#                     # print(f"#IP# process finished {time.time()-st}")
#                     self.cnt += 1
#                 time.sleep(0.01)
#             except Exception as e:
#                 print(e)
#                 self.isRun = False
#                 self.origin_video_writer.video_writer.release()
#                 self.result_video_writer.video_writer.release()
#                 print("-------- Close {}".format(self.host_name))
#
#     async def start_processing(self, frame):
#         st = time.time()
#         person_frame = frame.copy()
#         pose_frame = frame.copy()
#         obstacle_frame = frame.copy()
#         result = await asyncio.gather(self.person_detection(person_frame),
#                                       self.pose_detection(pose_frame),
#                                       self.obstacle_detection(obstacle_frame))
#
#         if result[0] is not None:
#             x1, y1, x2, y2 = result[0][1][0], result[0][1][1], result[0][1][2], result[0][1][3]
#             x1, x2 = int(x1 * 1.6), int(x2 * 1.6)
#             y1, y2 = int(y2 * 1.2), int(y2 * 1.2)
#             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
#             text = f"ID: {result[0][0]}"
#             cv2.putText(frame, text, (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 0, 255), 1)
#
#         if result[1] is not None:
#             text = f"Action : {result[1]}"
#             cv2.putText(frame, text, (2, 2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 0, 255), 1)
#
#         if result[2] is not None:
#             pass
#
#         self.result_video_writer.video_write(frame)
#         cv2.waitKey(1)
#         print(f'#IM# {time.time() - st}', result)
#         # await asyncio.gather(self.person_processing(results[0]),
#         #                      self.skeleton_processing(results[1]),
#         #                      self.obstacle_processing(results[2]))
#
#     async def person_detection(self, frame):
#         try:
#             return self.person_detector.run(frame)
#         except Exception as e:
#             print(f'# person detection error\n## {e}')
#             return None
#         # return None
#
#     async def pose_detection(self, frame):
#         try:
#             return self.action_ai_pose_detector.run_inference(frame)
#         except Exception as e:
#             print(f'# person detection error\n## {e}')
#             return None
#         # return []
#
#     async def obstacle_detection(self, frame):
#         return None
#
#     async def person_processing(self, person):
#         return None
#
#     async def skeleton_processing(self, skeleton):
#         return None
#
#     async def obstacle_processing(self, obstacle):
#         return None
