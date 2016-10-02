from ..units import *

class Vex393:
    STANDARD = 0
    HIGH_SPEED = 1
    TURBO = 2

    def __init__(self, gearing=STANDARD):
        self.nominal_voltage = Unit(7.2, Voltage.v)
        if gearing == self.STANDARD:
            self.free_speed = Unit(100, AngularVelocity.rpm)
            self.stall_torque = Unit(1.67, Torque.Nm)
            self.stall_current = Unit(4.8, Current.A)
            self.free_current = Unit(.37, Current.A)
        elif gearing == self.HIGH_SPEED:
            self.free_speed = Unit(160, AngularVelocity.rpm)
            self.stall_torque = Unit(1.04, Torque.Nm)
            self.stall_current = Unit(4.8
            self.free_current = Unit(.37
        elif gearing == self.TURBO:
            self.free_speed = Unit(240, AngularVelocity.rpm)
            self.stall_torque = Unit(0.7, Torque.Nm)
            self.stall_current = Unit(4.8, Current.A)
            self.free_current = Unit(.37, Current.A)
        else:
            raise Exception("Unknown option for Vex 393 motor")

    def get_speed(self, voltage, torque):
        pass
