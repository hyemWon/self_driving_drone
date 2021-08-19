import glob
import os


def remove_all_img():
    base_path = os.path.join(os.getcwd(), "imgs")

    for dir_name in os.listdir(base_path):
        dir_path = os.path.join(base_path, dir_name)
        for file_name in glob.glob(os.path.join(dir_path, '*.jpg')):
            os.remove(os.path.join(dir_path, file_name))
