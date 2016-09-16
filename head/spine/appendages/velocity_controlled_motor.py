class VelocityControlledMotor:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def drive(self, value):
        response = self.spine.send(self.devname, "vcmd {0:d} {1:d}".format(self.index, value))
        assert response == 'ok'

    def set(self, value):
        response = self.spine.send(self.devname, "vcdsv {0:d} {0:f}".format(self.index, value))
        assert response == 'ok'

    def getVelocity(self):
        response = self.spine.send(self.devname, "vcdgv {0:d}".format(self.index))
        return response

    def getPosition(self):
        response = self.spine.send(self.devname, "vcdgp {0:d}".format(self.index))
        return response

    def stop(self):
        response = self.spine.send(self.devname, "vcms {0:d}".format(self.index))
        assert response == 'ok'
