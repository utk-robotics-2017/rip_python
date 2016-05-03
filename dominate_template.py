# Python modules
import time
import logging
import argparse
import json
import os
import sys

# Local modules
from head.spine.core import get_spine
from head.spine.ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", required=False, help="Path to the config folder for the robot")
args = vars(ap.parse_args())

if args['config'] is None:
    config_folder = "config"
else:
    config_folder = args['config']

if not os.path.exists(config_folder + "/arduino_config.json"):
    sys.exit("Arduino Config File can not be found")

arduino_config_file = open(config_folder + "/arduino_config.json")
file_text = ""
for line in arduino_config_file:
    file_text += line

arduino_config = json.load(file_text)

ports = dict()
for arduino in arduino_config:
    ports[arduino['devname']] = arduino['port']

with get_spine(ports=ports, config=arduino_config) as s:
    class Robot:
        def __init__(self):
            return

        def start(self):
            return

    bot = Robot()
    bot.start()
