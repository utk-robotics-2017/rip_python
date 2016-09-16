class Encoder:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def read(self):
        '''
        Read the encoder.
        '''
        return float(self.spine.send(self.devname, "re {0:d}".format(self.index)))

    def zero(self):
        response = self.spine.send(self.devname, "ze {0:d}".format(self.index))
        assert response == 'ok'

    def pidGet(self):
        return self.read()
