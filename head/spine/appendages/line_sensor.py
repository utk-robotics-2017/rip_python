class LineSensor:
    def __init__(self, spine, devname, label, index, analog):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index
        self.analog = analog

    def read(self):
        if self.analog:
            return self.spine.send(self.devname, "rals {0:d}".format(self.index))
        else:
            return self.spine.send(self.devname, "rdls {0:d}".format(self.index))
