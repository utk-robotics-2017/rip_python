class Pid:

    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def modify_constants(self, kp, ki, kd):
        response = self.spine.send(
            self.devname, "pc {0:d} {1:f} {2:f} {3:f}".format(self.index, kp, ki, kd))
        assert response == 'ok'

    def set(self, setpoint):
        response = self.spine.send(
            self.devname, "ps {0:d} {0:f}".format(self.index, setpoint))
        assert response == 'ok'

    def off(self):
        response = self.spine.send(self.devname, "poff {0:d}".format(self.index))
        assert response == 'ok'

    def display(self):
        response = self.spine.send(self.devname, "pd {0:d}".format(self.index))
        # TODO: break response up into parts
        return response
