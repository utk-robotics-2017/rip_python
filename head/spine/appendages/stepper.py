from .component import Component


class Stepper(Component):
    SET_SPEED = "kSetStepperSpeed"
    STEP = "kStepStepper"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if not self.sim:
            self.setSpeedIndex = commands[self.SET_SPEED]
            self.stepIndex = commands[self.STEP]

    def get_command_parameters(self):
        yield self.setSpeedIndex, [self.SET_SPEED, "ii"]
        yield self.stepIndex, [self.STEP, "ii"]

    def setSpeed(self, value):
        '''
        Set speed for a stepper motor.
        :param value:
            Speed for the stepper to turn at
        :type value: ``int``
        '''
        if self.sim:
            return

        self.spine.send(self.devname, False, self.SET_SPEED, self.index, value)

    def step(self, value):
        '''
        Step the motor forward value amount

        :param value:
            Number of steps the motor will turn
        :type value: ``int``
        '''
        if self.sim:
            return

        self.spine.send(self.devname, False, self.STEP, self.index, value)
