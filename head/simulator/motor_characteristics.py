class Vex393:
    STANDARD = 0
    HIGH_SPEED = 1
    TURBO = 2

    def __init__(self, gearing=STANDARD):
        if gearing == self.STANDARD:
            self.free_speed = 100
            self.stall_torque = 1.67
            self.stall_current = 4.8
            self.free_current = .37
        elif gearing == self.HIGH_SPEED:
            self.free_speed = 160
            self.stall_torque = 1.04
            self.stall_current = 4.8
            self.free_current = .37
        elif gearing == self.TURBO:
            self.free_speed = 240
            self.stall_torque = 0.7
            self.stall_current = 4.8
            self.free_current = .37
        else:
            raise Exception("Unknown option for Vex 393 motor")

    def get_speed(self, voltage, torque):
        pass
