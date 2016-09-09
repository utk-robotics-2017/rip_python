class encoder:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def read(self):
        '''
        Read the encoder.
        '''
        return float(self.spine.send(self.devname, "re {}".format(self.index)))

    def zero(self):
        response = self.spine.send(self.devname, "ze {}".format(self.index))
        assert response == 'ok'

    def pidGet(self):
        return self.read()
