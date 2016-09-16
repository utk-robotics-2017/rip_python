class Switch:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def read(self):
        response = self.spine.send(self.devname, "rs {0:d}".format(self.index))
        return {'1': True, '0': False}[response]
