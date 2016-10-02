from .component import Component
from ...units import Unit, Angular


class Encoder(Component):
    READ = "kReadEncoder"
    READ_RESULT = "kReadEncoderResult"
    ZERO = "kZeroEncoder"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.ticks_per_rev = config['ticks_per_rev']
        self.sim = sim

        if self.sim:
            self.sim_velocity = 0
            self.sim_position = 0
        else:
            self.readIndex = commands[self.READ]
            self.readResultIndex = commands[self.READ_RESULT]
            self.zeroIndex = commands[self.ZERO]

    def get_command_parameters(self):
        yield self.readIndex, [self.READ, "i"]
        yield self.readResultIndex, [self.READ_RESULT, "l"]
        yield self.zeroIndex, [self.ZERO, "i"]

    def read(self):
        '''
        Read the encoder.
        '''
        # TODO: figure out...
        if self.sim:
            return self.sim_position

        response = self.spine.send(self.devname, True, self.READ, self.index)
        response = Unit(response[0] / self.ticks_per_rev, Angular.rev)

    def set_position(self, position):
        if self.sim:
            self.sim_position = position

    def set_velocity(self, velocity):
        if self.sim:
            self.sim_velocity = velocity

    def zero(self):
        if self.sim:
            self.sim_position = 0
            self.sim_velocity = 0
            return

        self.spine.send(self.devname, False, self.ZERO, self.index)

    def pidGet(self):
        return self.read()

    def sim_update(self, tm_diff):
        # TODO
        pass

    def get_hal_data(self):
        hal_data = {}
        hal_data['position'] = self.sim_position
        return hal_data
