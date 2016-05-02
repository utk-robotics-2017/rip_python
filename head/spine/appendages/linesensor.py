class linesensor:
    def __init__(self, spine, devname, label, index, analog):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index
        self.analog = analog

    def read(self):
        if self.analog:
            return self.spine.send(self.devname, "rals %d" % self.index)
        else:
            return self.spine.send(self.devname, "rdls %d" % self.index)
