import scanf
import logging
from ..spine.ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLLogger(__name__)


class SimCamera:
    def __init__(self, kwargs):
        self.sim_image = None
        self.sim_start = False

        if 'resolution' in kwargs:
            try:
                w, h = scanf.sscanf(kwargs['resolution'], "(%d, %d)")
                self.resolution = (w, h)
            except:
                logger.error("Unknown option for `resolution`. Format should be (w, h)")
                raise Exception("Unknown option for `resolution`. Format should be (w, h)")
        else:
            self.resolution = (320, 240)

    def start(self):
        self.sim_start = True

    def free(self):
        self.stop()

    def read(self):
        return self.sim_image

    def stop(self):
        self.sim_start = False

    def set_image(self, image):
        if self.sim_start:
            self.sim_image = image
