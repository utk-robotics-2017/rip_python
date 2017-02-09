from .component import Component
from ...units import *


class EasyStepper(Component):
    SET_SPEED = "kEasySetStepperSpeed"
    STEP = "kEasyStep"
    STEP_ANGLE = "kEasyStepAngle"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.angle_per_step = Angle(config['angle_per_step'], Angle.degree)
        self.sim = sim
        self.step_position = Constant(0)
        self.angle = Constant(0)

        if self.sim:
            self.sim_velocity = Constant(0)
        else:
            self.setSpeedIndex = commands[self.SET_SPEED]
            self.stepIndex = commands[self.STEP]
            self.stepAngleIndex = commands[self.STEP_ANGLE]

    def get_command_parameters(self):
        yield self.setSpeedIndex, [self.SET_SPEED, "ii"]
        yield self.stepIndex, [self.STEP, "ii"]
        yield self.stepAngleIndex, [self.STEP_ANGLE, "ii"]

    def set_speed(self, velocity):
        '''
        Set speed for a stepper motor.
        :param value:
            Speed for the stepper to turn at
        :type value: ``int``
        '''
        if self.sim:
            # Current sim assumption is instant move
            self.sim_velocity = velocity
            return

        self.spine.send(self.devname, False, self.SET_SPEED, self.index, velocity)

    def step_angle(self, angle):
        '''
        Set angle for a stepper motor
        :param angle:
            Angle to set the stepper to

        steps = (angle - self.angle) / self.angle_per_step
        self.step(steps)
        '''
        self.spine.send(self.devname, False, self.STEP_ANGLE, self.index, angle)
        self.angle = Angle(angle, angle.degree)

    def step(self, steps):
        '''
        Step the motor forward value amount

        :param value:
            Number of steps the motor will turn
        :type value: ``int``
        '''
        if self.sim:
            # Current sim assumption is instant move
            # TODO: add speed to simulation
            self.step_position += steps
            return

        self.spine.send(self.devname, False, self.STEP, self.index, value)
        self.angle += Constant(steps) * self.angle_per_step

    def sim_update(self, tm_diff):
        pass

    def get_hal_data(self):
        hal_data = {}
        hal_data['velocity'] = self.sim_velocity
        hal_data['step_position'] = self.step_position
        hal_data['angle'] = self.angle
        return hal_data
