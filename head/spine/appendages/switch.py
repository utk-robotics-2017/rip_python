class switch:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def read(self):
        return self.spine.send(self.devname, "rs %d" % self.index)
