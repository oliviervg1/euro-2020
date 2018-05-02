from configparser import ConfigParser


def read_config(config_path):
    config = ConfigParser()
    config.read(config_path)
    return config
