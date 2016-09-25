from threading import Thread
import math
import logging

from head.spine.ourlogging import setup_logging
from head.controllers.PID import PID
from head.controllers.VPID import VPID

setup_logging(__file__)
logger = logging.getLogger(__name__)


class PIDController:

    def __init__(self, type='position', kp=0.0, ki=0.0, kd=0.0,
                 output_max=0.0, output_min=0.0, input_sources=None,
                 output_sources=None, reverse=None, tolerance=1):
        if(type == 'position'):
            self.PID = PID(kp, ki, kd, output_max, output_min)
        else:
            self.PID = VPID(kp, ki, kd, output_max, output_min)

        self.input_sources = input_sources
        self.output_sources = output_sources
        self.reverse = reverse
        self.stopped = False
        self.tolerance = tolerance

    def start(self):
        # start the process to run the pid
        if self.stopped:
            self.stopped = False
            t = Thread(target=self.update, args=())
            t.start()

    def update(self):
        while not self.stopped:
            self.calculate()

    def stop(self):
        self.stopped = True

    def set_setpoint(self, value):
        self.PID.set_setpoint(value)

    def calculate(self):
        if isinstance(self.input_sources, list):
            input_ = 0.0
            for input_source in self.input_sources:
                input_ += input_source.pid_gGet()
        else:
            input_ = self.input_source.pid_get()

        self.output_ = self.PID.calculate(input_)

        # outputSources is None if this PIDController is chained to another PIDController
        if self.output_sources is not None:
            # outputSources is a list if multiple outputs are set to follow one input
            if isinstance(self.output_sources, list):
                if self.reverse is not None:
                    for output_source, reverse in self.output_sources, self.reverse:
                        if reverse:
                            output_source.pid_set(-self.output_)
                        else:
                            output_source.pid_set(self.output_)
                else:
                    for output_source in self.output_sources:
                        output_source.pid_set(-self.output_)
            # single input to single output
            else:
                if reverse is not None or not reverse:
                    self.outputSources.pid_set(self.output_)
                else:
                    self.outputSources.pid_set(-self.output_)
        return self.output_

    # used for chaining pid controllers
    def pid_get(self):
        return self.output_

    def is_finished(self):
        return math.abs(self.output_) < self.tolerance
