from ..units import *

class Vex393:
    STANDARD = 0
    HIGH_SPEED = 1
    TURBO = 2

    def __init__(self, gearing=STANDARD):
        self.nominal_voltage = Voltage(7.2, Voltage.v)
        if gearing == self.STANDARD:
            self.free_speed = AngularVelocity(100, AngularVelocity.rpm)
            self.stall_torque = Torque(1.67, Torque.Nm)
            self.stall_current = Current(4.8, Current.A)
            self.free_current = Current(.37, Current.A)
        elif gearing == self.HIGH_SPEED:
            self.free_speed = AngularVelocity(160, AngularVelocity.rpm)
            self.stall_torque = Torque(1.04, Torque.Nm)
            self.stall_current = Current(4.8, Current.A)
            self.free_current = Current(.37, Current.A)
        elif gearing == self.TURBO:
            self.free_speed = AngularVelocity(240, AngularVelocity.rpm)
            self.stall_torque = Torque(0.7, Torque.Nm)
            self.stall_current = Current(4.8, Current.A)
            self.free_current = Current(.37, Current.A)
        else:
            raise Exception("Unknown option for Vex 393 motor")

    def get_speed(self, voltage, torque):
        # P = I*V = w*t
        # w = I * V / t
        return Velocity(0, Velocity.inch_s)
