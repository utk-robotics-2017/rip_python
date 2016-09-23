from .component import Component


class Encoder(Component):
    READ = "kReadEncoder"
    READ_RESULT = "kReadEncoderResult"
    ZERO = "kZeroEncoder"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if not self.sim:
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
            return 0

        return float(self.spine.send(self.devname, True, self.READ, self.index))

    def zero(self):
        # TODO: figure out...
        if self.sim:
            return

        self.spine.send(self.devname, False, self.ZERO, self.index)

    def pidGet(self):
        return self.read()
