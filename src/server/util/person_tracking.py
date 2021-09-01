import cv2
import datetime
import imutils
import numpy as np
import os
from .centroidtracker import CentroidTracker
from .writer import ImageWriter
from .data import Data


class PersonTracker:
    def __init__(self):
        self.name = 'person'
        self.proto_path = os.path.join(os.getcwd(), "util/mobilenet/MobileNetSSD_deploy.prototxt")
        self.model_path = os.path.join(os.getcwd(), "util/mobilenet/MobileNetSSD_deploy.caffemodel")
        self.write_path = os.path.join(os.getcwd(), "imgs", self.name)

        self.detector = cv2.dnn.readNetFromCaffe(prototxt=self.proto_path, caffeModel=self.model_path)
        self.data = Data().instance()
        # Only enable it if you are using OpenVino environment
        # detector.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)
        # detector.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        self.CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                        "sofa", "train", "tvmonitor"]

        self.tracker = CentroidTracker(maxDisappeared=80, maxDistance=90)
        self.objectId = 0
        self.frame_cnt = 0
        self.person_crops = []

    def non_max_suppression_fast(self, boxes, overlapThresh):
        try:
            if len(boxes) == 0:
                return []

            if boxes.dtype.kind == "i":
                boxes = boxes.astype("float")

            pick = []

            x1 = boxes[:, 0]
            y1 = boxes[:, 1]
            x2 = boxes[:, 2]
            y2 = boxes[:, 3]

            area = (x2 - x1 + 1) * (y2 - y1 + 1)
            idxs = np.argsort(y2)

            while len(idxs) > 0:
                last = len(idxs) - 1
                i = idxs[last]
                pick.append(i)

                xx1 = np.maximum(x1[i], x1[idxs[:last]])
                yy1 = np.maximum(y1[i], y1[idxs[:last]])
                xx2 = np.minimum(x2[i], x2[idxs[:last]])
                yy2 = np.minimum(y2[i], y2[idxs[:last]])

                w = np.maximum(0, xx2 - xx1 + 1)
                h = np.maximum(0, yy2 - yy1 + 1)

                overlap = (w * h) / area[idxs[:last]]

                idxs = np.delete(idxs, np.concatenate(([last],
                                                       np.where(overlap > overlapThresh)[0])))

            return boxes[pick].astype("int")
        except Exception as e:
            print("Exception occurred in non_max_suppression : {}".format(e))

    def run(self, frame):
        frame = imutils.resize(frame, width=600)

        (H, W) = frame.shape[:2] # 450 600
        # print(frame.shape) # (450, 600, 3)

        # blob 이미지 생성
        # 파라미터
        # 1) image : 사용할 이미지
        # 2) scalefactor : 이미지 크기 비율 지정
        # 3) size : Convolutional Neural Network에서 사용할 이미지 크기를 지정
        # 4) mean : Mean Subtraction 값을 RGB 색상 채널별로 지정해 주는 경험치 값(최적의 값)
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
        # print(blob)
        # [[[[-0.1137235  -0.1372525  -0.1137235  ...  0.5764605   0.5843035
        #      0.5843035 ] ....

        # 사람 인식
        self.detector.setInput(blob)
        person_detections = self.detector.forward() # caffe 모델이 처리한 결과값 : 4차원 배열
        # print(person_detections.shape) # (1, 1, 100, 7)

        rects = []
        # 사람인식 수 만큼 반복
        for i in np.arange(0, person_detections.shape[2]):
            # 사람 확률 추출
            confidence = person_detections[0, 0, i, 2]

            # 사람 확률이 0.4보다 큰 경우
            if confidence > 0.4:
                # 인식된 사람 index
                idx = int(person_detections[0, 0, i, 1])

                # print(int(person_detections[0, 0, i, 1])) # 15

                if self.CLASSES[idx] != "person":
                    continue

                # bounding box 위치 계산
                person_box = person_detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                (startX, startY, endX, endY) = person_box.astype("int")
                # print(person_box)
                rects.append(person_box)

        boundingboxes = np.array(rects)
        boundingboxes = boundingboxes.astype(int)
        rects = self.non_max_suppression_fast(boundingboxes, 0.3)

        objects = self.tracker.update(rects)

        self.data.lock.acquire()
        certification_Id = self.data.certification_Id
        self.data.lock.release()

        # ---- with certification
        # if certification_Id < 0:
        #     # 인증되기 전에는 검출된 모든 사람의 박스 출력
        #     for (objectId, bbox) in objects.items():
        #         x1, y1, x2, y2 = bbox
        #         x1 = int(x1)
        #         y1 = int(y1)
        #         x2 = int(x2)
        #         y2 = int(y2)
        #
        #         text = "ID: {}".format(objectId)
        #         cv2.putText(frame, text, (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
        #         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # else:
        #     # 인증 되고 나서는 해당 사람만 박싱해서 보여준다.
        #     x1, y1, x2, y2 = objects[certification_Id]
        #     text = f"ID: {certification_Id}"
        #     cv2.putText(frame, text, (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
        #     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # -- no certification
        for (objectId, bbox) in objects.items():
            x1, y1, x2, y2 = bbox
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            text = "ID: {}".format(objectId)
            cv2.putText(frame, text, (x1, y1-5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)

            # 만약 사용자가 손을 든다면 (openpose)
            # 그 사용자의 objectID를 기억해서 그 사용자만 추적하기(?)
            if objectId == 2:
                # bounding box 출력
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                # text = "ID: {}".format(objectId)
                cv2.putText(frame, text, (x1, y1-5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)

        # frame write
        cv2.imwrite(os.path.join(self.write_path, f"frame{self.frame_cnt}.jpg"), frame)
        self.frame_cnt += 1
        # cv2.waitKey(1)

        if len(objects) > 0:
            if certification_Id >= 0:   # Pass certification
                return [objects[certification_Id]]
            else:
                return [objects]
        else:
            return None
