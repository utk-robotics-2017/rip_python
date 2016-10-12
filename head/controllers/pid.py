import logging

from head.spine.ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)


class PID:
    """
    Discrete PID control
    """

    def __init__(self, P=0.0, I=0.0, D=0.0, output_max=0.0, output_min=0.0):

        self.kP = P
        self.kI = I
        self.kD = D
        self.output_max = output_max
        self.output_min = output_min

        self.integrator = 0.0

        self.setpoint = 0.0
        self.last_error = 0.0

    def update(self, current_value):
        """
        Calculate PID output value for given reference input and feedback
        """

        error = self.setpoint - current_value

        p = self.kP * error

        self.integrator += error
        if self.integrator > self.output_max:
            self.integrator = self.output_max
        elif self.integrator < self.output_min:
            self.integrator = self.output_min
        i = self.integrator * self.kI

        d = self.kD * (error - self.last_error)
        self.last_error = error

        output = p + i + d

        if output > self.output_max:
            output = self.output_max
        elif self.integrator < self.output_min:
            output = self.output_min

        return output

    def set_setpoint(self, setpoint):
        """
        Initilize the setpoint of PID
        """
        self.setpoint = setpoint
        self.integrator = 0
        self.last_error = 0

    def setKp(self, P):
        self.kP = P

    def setKi(self, I):
        self.kI = I

    def setKd(self, D):
        self.kD = D

    def get_setpoint(self):
        return self.setpoint

    def reset(self):
        self.last_error = 0
        self.integrator = 0
