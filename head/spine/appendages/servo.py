class servo:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def set(self, value):
        self.spine.send(self.devname, "ss %d %d" % (self.index, value))
