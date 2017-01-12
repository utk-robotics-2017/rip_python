from .component import Component
from ...units import *


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
            self.sim_velocity = Constant(0)
            self.sim_position = Constant(0)
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
        return Angle(response[0] / self.ticks_per_rev, Angle.rev)

    def set_position(self, position):
        if self.sim:
            self.sim_position = position

    def set_velocity(self, velocity):
        if self.sim:
            self.sim_velocity = velocity

    def zero(self):
        if self.sim:
            self.sim_position = Constant(0)
            self.sim_velocity = Constant(0)
            return

        self.spine.send(self.devname, False, self.ZERO, self.index)

    def pidGet(self):
        return self.read()

    def test(self):
        print("\nEncoder\n")

        init = self.read()
        print("Initial reading: " + init)
        print("Move the wheel manually")
        change = self.read()
        print("New reading: " + change)
        
        while True:
            f_query = raw_input("Is this correct? (y/n): ")
            if f_query == 'y' or f_query == 'n':
                break
    def sim_update(self, hal_data, tm_diff):
        self.sim_position = self.sim_velocity * tm_diff

    def get_hal_data(self):
        hal_data = {}
        hal_data['position'] = self.sim_position
        return hal_data
