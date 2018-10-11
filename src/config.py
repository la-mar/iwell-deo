import yaml
import os
from pprint import pprint

# config = {} # configuration dictionary

# %% Load Configuration

# with open("Flowback\\config.yaml", 'r') as stream:
#     try:
#         config = (yaml.load(stream))
#     except yaml.YAMLError as exc:
#         print(exc)
# pprint(dir(yaml.dump))

# def get_config():

#     pprint(config)

#     return config

class Config(dict):
    """
    https://codereview.stackexchange.com/questions/186653/pyyaml-saving-data-to-yaml-files

    """
    def __init__(self, filename = None):
        if filename is None:
            filename = "config.yaml"
        self.filename = filename
        if os.path.isfile(filename):
            with open(filename) as f:
                # use super here to avoid unnecessary write
                super(Config, self).update(yaml.load(f) or {})

    def __setitem__(self, key, value):
        super(Config, self).__setitem__(key, value)
        with open(self.filename, "w") as f:
            yaml.dump(self, f, default_flow_style=False)

    def __delitem__(self, key):
        super(Config, self).__delitem__(key)
        with open(self.filename, "w") as f:
            yaml.dump(self, f, default_flow_style=False)

    def update(self, kwargs):
        super(Config, self).update(kwargs)
        with open(self.filename, "w") as f:
            yaml.dump(self, f, default_flow_style=False)

Config()






# %lsmagic

# %whos