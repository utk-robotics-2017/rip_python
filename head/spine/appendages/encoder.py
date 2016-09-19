class Encoder:
    READ = "kReadEncoder"
    READ_RESULT = "kReadEncoderResult"
    ZERO = "kZeroEncoder"

    def __init__(self, spine, devname, config, commands):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']

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
        return float(self.spine.send(self.devname, True, self.READ, self.index))

    def zero(self):
        self.spine.send(self.devname, False, self.ZERO, self.index)

    def pidGet(self):
        return self.read()
