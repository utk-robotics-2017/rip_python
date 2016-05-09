from multiprocessing import Process
import math

from head.spine.ourlogging import setup_logging
from head.controllers.PID import PID
from head.controllers.VPID import VPID

setup_logging(__file__)
logger = logging.getLogger(__name__)


class PIDController:
    def __init__(self, type='position', P=0.0, I=0.0, D=0.0, outputMax=0.0, outputMin=0.0, inputSources=None, outputSources=None, reverse=None, tolerance=1):
        if(type == 'position'):
            self.PID = PID(P, I, D, outputMax, outputMin)
        else:
            self.PID = VPID(P, I, D, outputMax, outputMin)

        self.inputSources = inputSources
        self.outputSources = outputSources
        self.reverse = reverse
        self.stopped = False
        self.tolerance = tolerance

    def start(self):
        # start the process to run the pid
        if self.stopped:
            self.stopped = False
            p = Process(target=self.update, args=())
            p.start()

    def update(self):
        while True:
            if self.stopped:
                return
            self.calculate()

    def stop(self):
        self.stopped = True

    def setPoint(self, value):
        self.PID.setPoint(value)

    def calculate(self):

        if isinstance(self.inputSources, list):
            input_ = 0.0
            for inputSource in self.inputSources:
                input_ += inputSource.pidGet()
        else:
            input_ = self.inputSource.pidGet()

        self.output_ = self.PID.calculate(input_)

        # outputSources is None if this PIDController is chained to another PIDController
        if not self.outputSources is None:
            # outputSources is a list if multiple outputs are set to follow one input
            if isinstance(self.outputSources, list):
                if not self.reverse is None:
                    for outputSource, reverse in self.outputSources, self.reverse:
                        if reverse:
                            self.outputSources.pidSet(-self.output_)
                        else:
                            self.outputSources.pidSet(self.output_)
                else:
                    for outputSource in self.outputSources:
                        self.outputSources.pidSet(-self.output_)
            # single input to single output
            else:
                if not reverse is None or not reverse:
                    self.outputSources.pidSet(self.output_)
                else:
                    self.outputSources.pidSet(-self.output_)

    # used for chaining pid controllers
    def pidGet(self):
        return self.output_

    def isFinished(self):
        return math.abs(self.output_) < self.tolerance
