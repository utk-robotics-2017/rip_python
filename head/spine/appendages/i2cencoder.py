class i2cencoder:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index
        self.pidSource = 'position'

    def setPidSource(self, source):
        self.pidSource = source

    def position(self):
        return float(self.spine.send(self.devname, "ep %d" % self.index))

    def raw_position(self):
        return float(self.spine.send(self.devname, "erp %d" % self.index))

    def speed(self):
        return float(self.spine.send(self.devname, "es %d" % self.index))

    def velocity(self):
        return float(self.spine.send(self.devname, "ev %d" % self.index))

    def zero(self):
        response = self.spine.send(self.devname, "ez %d" % self.index)
        assert response == 'ok'

    def pidGet(self):
        if self.pidSource == 'position':
            return self.position()
        elif self.pidSource == 'velocity':
            return self.velocity()
