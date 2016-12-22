class ElectronicComponentDetector:
    DECODE = "kDecode"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devnam = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if sim:
            pass
        else:
            self.decodeIndex = commands[self.DECODE]

    def get_command_parameters(self):
        yield self.decodeIndex, [self.DECODE, "c"]

    def decode(self, pad='9'):
        response = self.spine.send(self.devname, True, self.DECODE, self.index, pad)
        return response
