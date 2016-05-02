class i2cencoder:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def position(self):
        return self.spine.send(self.devname, "ep %d" % self.index)

    def raw_position(self):
        return self.spine.send(self.devname, "erp %d" % self.index)

    def speed(self):
        return self.spine.send(self.devname, "es %d" % self.index)

    def zero(self):
        self.spine.send(self.devname, "ez %d" % self.index)
