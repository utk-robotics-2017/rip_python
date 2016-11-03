from ..units import *


class VexServo:
    def __init__(self):
        self.max_angle = Angle(100, Angle.degree)

    def get_position(self, value):
        return self.max_angle * Constant(value / 255)
