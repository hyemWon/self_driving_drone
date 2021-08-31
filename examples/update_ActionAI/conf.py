# Choose your classifier
from sklearn.linear_model import LogisticRegression as classifier

# Set source for opencv VideoCapture: usb index, mp4, rtsp
stream = 0

# Set path to staged data, raw images, pickled sklearn model
csv_path = 'data/data.csv'
# images_dir = 'path/to/images/dir'
images_dir = '/home/piai/yolo-action-recognition/dataset/agu_faint'
classifier_model = 'models/classifier.sav'



