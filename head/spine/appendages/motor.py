class motor:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def drive(self, value):
        if value == 0:
            self.stop()
            return
        response = self.spine.send(self.devname, "mod {} {}".format(self.index, value))
        assert response == 'ok'

    def stop(self):
        response = self.spine.send(self.devname, "mod {}".format(self.index))
        assert response == 'ok'

    def pidSet(self, value):
        self.drive(value)
