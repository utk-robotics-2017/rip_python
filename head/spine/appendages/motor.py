class Motor:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def drive(self, value):
        if value == 0:
            self.stop()
            return
        response = self.spine.send(self.devname, "mod {0:d} {1:d}".format(self.index, value))
        assert response == 'ok'

    def stop(self):
        response = self.spine.send(self.devname, "mos {0:d}".format(self.index))
        assert response == 'ok'

    def pidSet(self, value):
        self.drive(value)
