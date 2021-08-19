import argparse
import configparser


class Parser:
    @classmethod
    def socket_argparser(cls):
        parser = argparse.ArgumentParser(description="")
        parser.add_argument("--host", type=str, default="114.223.122.51",)
        # parser.add_argument("--port", type=int, default=)

        return parser.parse_args()

    @classmethod
    def config_parsing(cls):
        return configparser.ConfigParser()
