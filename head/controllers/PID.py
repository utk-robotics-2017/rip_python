from head.spine.ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)


class PID:
    """
    Discrete PID control
    """

    def __init__(self, P=0.0, I=0.0, D=0.0, outputMax=0.0, outputMin=0.0):

        self.kP = P
        self.kI = I
        self.kD = D
        self.outputMax = outputMax
        self.outputMin = outputMin

        self.integrator = 0.0

        self.set_point = 0.0
        self.last_error = 0.0

    def update(self, current_value):
        """
        Calculate PID output value for given reference input and feedback
        """

        error = self.set_point - current_value

        p = self.kP * error

        self.integrator += error
        if self.integrator > self.outputMax:
            self.integrator = self.outputMax
        elif self.integrator < self.outputMin:
            self.integrator = self.outputMin
        i = self.integrator * self.kI

        d = self.kD * (error - self.last_error)
        self.last_error = error

        output = p + i + d

        if output > self.outputMax:
            output = self.outputMax
        elif self.integrator < self.outputMin:
            output = self.outputMin

        return output

    def setPoint(self, set_point):
        """
        Initilize the setpoint of PID
        """
        self.set_point = set_point
        self.integrator = 0
        self.last_error = 0

    def setKp(self, P):
        self.kP = P

    def setKi(self, I):
        self.kI = I

    def setKd(self, D):
        self.kD = D

    def getPoint(self):
        return self.set_point

    def reset(self):
        self.last_error = 0
        self.integrator = 0
