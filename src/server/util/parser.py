import argparse
import configparser
import yaml
import importlib
from easydict import EasyDict as edict


class ConfigParser:
    __config = None

    @classmethod
    def load_config(cls, path, file_type, is_edict=True):
        conf = None
        if file_type == 'yaml':
            with open(path, 'r') as f:
                conf = yaml.load(f, Loader=yaml.FullLoader)
        elif file_type == 'ini' or file_type == 'conf':
            with open(path, 'r') as f:
                conf = configparser.ConfigParser()
        elif file_type == 'py':
            conf = importlib.import_module(path)

        if is_edict:
            conf = edict(conf)

        return conf

    @classmethod
    def save_config(cls, config, path):
        with open(path, 'w') as f:
            config.write(f)

    @classmethod
    def get_config(cls):
        return cls.__config


# class ArgParser:
#     @classmethod
#     def parse_arg(cls, path):
#         parser = argparse.ArgumentParser(description="")
#         parser.add_argument("--host", type=str, default="114.223.122.51")
#         # parser.add_argument("--port", type=int, default=)
#
#         return parser.parse_args()


# if __name__ == '__main__':
#     ConfigParser.load_config('', 'yaml')
#     conf = ConfigParser.get_config()
#     print(conf)
