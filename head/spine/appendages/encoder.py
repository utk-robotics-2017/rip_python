class encoder:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def read(self):
        return self.spine.send(self.devname, "re %d" % self.index)

    def zero(self):
        self.spine.send(self.devname, "ze %d" % self.index)
