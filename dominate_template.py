# Python modules
import time
import logging
import argparse

# Local modules
from head.spine.core import get_spine
from head.spine.ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)


class get_robot:
    def __init__(self, sim=False):
        self.sim = sim

    def __enter__(self):
        self.gs = get_spine(sim=self.sim)
        self.r = Robot(self.gs.__enter__())
        return self.r

    def __exit__(self, type, value, traceback):
        self.gs.__exit__(type, value, traceback)


class Robot:
    def __init__(self, s):
        self.s = s

    def start(self):
        pass

if __name__ == "__main__":
    with get_robot(True) as bot:
        bot.start()
