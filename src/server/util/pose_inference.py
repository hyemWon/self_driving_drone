import os
import pickle
from .actionai.transformer import PoseExtractor

from .data import Data


class ActionAIPoseDetector:
    def __init__(self):
        self.name = 'Action AI Pose Detector'
        self.data = Data().instance()

        self.conf_path = os.path.join(os.getcwd(), 'util/actionai/conf')
        self.write_path = os.path.join(os.getcwd(), "imgs", "pose")
        self.model_path = os.path.join(os.getcwd(), 'util/actionai/models/model.tflite')

        self.classifier_path = os.path.join(os.getcwd(), 'util/actionai/models/classifier.sav')

        self.model = pickle.load(open(self.classifier_path, 'rb'))
        self.extractor = PoseExtractor(model_path=self.model_path)

        self.actions = ['certification', 'violence', 'fainting']
        self.count = 0
        self.gather = 8
        self.pred = []

    def run_inference(self, frame, object_id=None):
        self.count += 1

        # cv2.imshow('Crime Detection', frame)
        sample = self.extractor.transform([frame])
        prediction = self.model.predict(sample.reshape(1, -1))
        self.pred.append(prediction[0])

        if self.count == self.gather:
            pose = self.most_frequent()
            pred_percent = self.model.predict_proba(sample.reshape[1, -1])

            if pose in self.actions:
                self.lock.acquire()
                self.data.pose = pose
                self.lock.release()

            self.count = 0
            self.pred = []

            print(f"## {pose} pose detected!! {pred_percent}")
            return pose

        # cv2.imwrite(os.path.join(self.write_path, f"frame{self.count}.jpg"), frame)

        return None

    def most_frequent(self):
        count_list = []
        for x in self.pred:
            count_list.append(self.pred.count(x))

        max_idx = count_list.index(max(count_list))
        return self.pred[max_idx]