class vpid:

    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def modify_constants(self, kp, ki, kd):
        response = self.spine.send(
            self.devname, "vpc {0:d} {1:f} {2:f} {3:f}".format(self.index, kp, ki, kd))
        assert response == 'ok'

    def set(self, setpoint):
        response = self.spine.send(
            self.devname, "vps {0:d} {1:f}".format(self.index, setpoint))
        assert response == 'ok'

    def off(self):
        response = self.spine.send(self.devname, "vpoff {0:d}".format(self.index))
        assert response == 'ok'

    def display(self):
        response = self.spine.send(self.devname, "vpd {0:d}".format(self.index))
        # TODO: break response up into parts
        return response
