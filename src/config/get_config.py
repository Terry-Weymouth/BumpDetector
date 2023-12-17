from pathlib import Path
import yaml


def get_database_access():
    config_file = Path.home().joinpath("config").joinpath("database_access.yaml")
    content = yaml.safe_load(open(config_file,'r'))
    return content


def get_mapgl_access():
    config_file = Path.home().joinpath("config").joinpath("mapgl_access.yaml")
    content = yaml.safe_load(open(config_file,'r'))
    return content

