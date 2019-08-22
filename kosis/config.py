# -*- coding: utf-8 -*-

import os.path
from configparser import ConfigParser, NoSectionError

__all__ = [
    "get_apikey",
    "set_apikey",
]

config_dirname = "~/.kosis"
config_filename = "kosis.ini"


def get_config_filepath():
    config_dir = os.path.expanduser(config_dirname)
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)
    config_filepath = os.path.join(config_dir, config_filename)
    if not os.path.exists(config_filepath):
        with open(config_filepath, "w") as config_file:
            config_file.write("[api]\nkey = ")
        set_apikey()
    return config_filepath


def get_apikey():
    config_filepath = get_config_filepath()
    config = ConfigParser()
    config.read(config_filepath)
    try:
        key = config.get("api", "key")
    except NoSectionError as e:
        with open(config_filepath, "w") as config_file:
            config_file.write("[api]\nkey = ")
        raise e
    return key


def set_apikey(key=""):
    config_filepath = get_config_filepath()
    config = ConfigParser()
    config.read(config_filepath)
    config.set("api", "key", key)
    with open(config_filepath, "w") as config_file:
        config.write(config_file)
