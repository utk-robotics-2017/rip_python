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
    def __enter__(self):
        self.gs = get_spine()
        self.r = Robot(self.gs.__enter__())
        return self.r

    def __exit__(self, type, value, traceback):
        self.gs.__exit__(type, value, traceback)


class Robot:
    def __init__(self, s):
        self.s = s

    def start(self):
        logger.info("info")
        logger.debug("debug")
        logger.warning("warning")
        logger.error("error")
        logger.critical("critical")

if __name__ == "__main__":
    with get_robot() as bot:
        bot.start()
