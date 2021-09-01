import os
import pickle
from .actionai.transformer import PoseExtractor

from .data import Data


class ActionAIPoseDetector:
    def __init__(self):
        self.name = 'Action AI Pose Detector'
        # self.data = Data().instance()
        # self.lock = self.data.lock

        self.conf_path = os.path.join(os.getcwd(), 'util/actionai/conf')
        self.write_path = os.path.join(os.getcwd(), "imgs", "pose")

        # self.certification_classifier_path = os.path.join(os.getcwd(), 'util/actionai/models/classifier_certification.sav')
        # self.certification_model_path = os.path.join(os.getcwd(), 'util/actionai/models/pose.tflite')
        # self.certification_model = pickle.load(open(self.certification_classifier_path, 'rb'))
        # self.certification_extractor = PoseExtractor(model_path=self.certification_model_path)
        #
        # self.assult_classifier_path = os.path.join(os.getcwd(), 'util/actionai/models/classifier.sav')
        # self.assult_model_path = os.path.join(os.getcwd(), 'util/actionai/models/model.tflite')
        # self.assult_model = pickle.load(open(self.assult_classifier_path, 'rb'))
        # self.assult_extractor = PoseExtractor(model_path=self.assult_model_path)

        self.actions = ['certification', 'violence', 'fainting']
        self.count = 0
        self.gather = 10
        self.pred = []

        self.state = 'certification'

    def run_inference(self, frame, ob):
        self.count += 1

        if self.state == 'certification':
            sample = self.certification_extractor.transform([frame])
            prediction = self.certification_model.predict(sample.reshape(1, -1))
        else:
            sample = self.assult_extractor.transform([frame])
            prediction = self.certification_model.predict(sample.reshape(1, -1))
        self.pred.append(prediction[0])

        if self.count == self.gather:
            pose = self.most_frequent()

            if pose == 'certification':
                self.state = 'assult'

            self.count = 0
            self.pred = []

            print(f"## {pose} pose detected!!")
            return pose

        return None

    def most_frequent(self):
        count_list = []
        for x in self.pred:
            count_list.append(self.pred.count(x))

        max_idx = count_list.index(max(count_list))
        return self.pred[max_idx]
