from .component import Component


class Encoder(Component):
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
