class ElectronicComponentDetector:
    DECODE = "kDecode"
    DECODE_RESULT = "kDecodeResult"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if sim:
            pass
        else:
            self.decodeIndex = commands[self.DECODE]
            self.decodeResultIndex = commands[self.DECODE_RESULT]

    def get_command_parameters(self):
        yield self.decodeIndex, [self.DECODE, "c"]
        yield self.decodeResultIndex, [self.DECODE_RESULT, "ccccc"]

    def decode(self, pad='9'):
        response = self.spine.send(self.devname, True, self.DECODE, pad)
        return response
