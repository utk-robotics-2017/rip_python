from .component import Component
from ...simulator.sim_servo import *


class Servo(Component):
    SET = "kSetServo"
    DETACH = "kDetachServo"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if sim:
            if config['type'].lower() == "vex":
                self.sim_servo = VexServo()
            self.sim_value = 0
            self.sim_position = 0
            self.sim_attached = False
        else:
            self.setIndex = commands[self.SET]
            self.detachIndex = commands[self.DETACh]

    def get_command_parameters(self):
        yield self.setIndex, [self.SET, "ii"]
        yield self.detachIndex, [self.DETACH, "i"]

    def set(self, value):
        '''
        Set each servo to a position.
        Programming with this command can be tricky since often the servos are
        reverse to each other and they can also fight against each other when
        they are set to different positions.
        :param value:
            Position from 0 to 255 of the servo.
        :type value: ``int``
        '''
        if self.sim:
            self.sim_attached = True
            self.sim_value = value
            self.sim_position = self.sim_servo.get_position(value)
            return

        assert 0 <= value <= 255
        self.spine.send(self.devname, False, self.SET, self.index, value)

    def detach(self):
        if self.sim:
            self.sim_attached = False
            return

        self.spine.send(self.devname, False, self.DETACH, self.index)

    def sim_update(self, tm_diff):
        pass

    def get_hal_data(self):
        hal_data = {}
        hal_data['value'] = self.sim_value
        hal_data['position'] = self.sim_position
        hal_data['attached'] = self.sim_attached
        return hal_data
