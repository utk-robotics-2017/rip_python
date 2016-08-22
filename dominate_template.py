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



with get_spine() as s:
    class Robot:
        def __init__(self):
            return

        def start(self):
            return

    bot = Robot()
    bot.start()
